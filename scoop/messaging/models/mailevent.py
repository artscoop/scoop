# coding: utf-8
import datetime
from smtplib import SMTPException, SMTPResponseException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail.message import EmailMultiAlternatives
from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from pretty_times import pretty
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.uuid import UUID128Model
from scoop.core.util.data.textutil import one_line
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.django.templateutil import render_block_to_string
from scoop.core.util.model.model import SingleDeleteQuerySetMixin
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.request import default_context


class MailEventQuerySetMixin(object):
    """ Mixin de manager des événements mail """

    # Getter
    def discardable(self, user):
        """
        Renvoyer les événements supprimables si l'utilisateur passe en ligne
        :type self: django.db.models.Queryset
        """
        return self.filter(recipient=user, forced=False, sent=False)

    def orphans(self):
        """
        Renvoyer les événements dont le statut est incorrect
        :type self: django.db.models.Queryset
        """
        return self.filter(recipient__isnull=True)

    def discard(self):
        """
        Marquer comme annulés les événements mails du queryset

        :type self: django.db.models.Queryset
        """
        return self.update(discarded=True)


class MailEventQuerySet(models.QuerySet, MailEventQuerySetMixin, SingleDeleteQuerySetMixin):
    """ Queryset des fils de discussion """
    pass


class MailEventManager(models.Manager.from_queryset(MailEventQuerySet), models.Manager, SingleDeleteQuerySetMixin, MailEventQuerySetMixin):
    """ Manager des événements mail """

    def get_queue_length(self):
        """ Renvoyer le nombre d'événements en file """
        return self.filter(sent=False, discarded=False).count()

    def unsent(self):
        """ Renvoyer les événements non expédiés """
        return self.filter(sent=False, discarded=False)

    def get_unsent_count(self):
        """ Renvoyer le nombre d'événements non expédiés """
        return self.unsent().count()

    # Setter
    def _send_mail(self, sender, to, title, text, html=None):
        """ Envoyer immédiatement un courrier """
        message = EmailMultiAlternatives(title, text, sender, make_iterable(to))
        if html is not None:
            message.attach_alternative(html, "text/html")
        try:
            message.send()
            return True
        except (SMTPException, SMTPResponseException):
            return False

    def queue(self, recipient, typename, data=None, forced=False):
        """
        Mettre en file un événement mail

        :param recipient: utilisateur ou email
        :param typename: type d'email enregistré (voir MailType) ex. 'messaging.message.staff'
        :param data: données à attacher au mail
        :param forced: indique si le mail fait partie des contenus prioritaires
        :type data: dict
        :type forced: bool
        :type recipient: str | User
        :type typename: str
        """
        from scoop.messaging.models.mailtype import MailType
        # Convertir les éléments du dictionnaire passé en listes
        data = dict() if data is None else data
        mail_data = {item: make_iterable(data[item]) for item in data}
        # Créer ou récupérer un événement mail
        mail_type = MailType.objects.get_named(typename)
        kwargs = {'sent_email': recipient} if isinstance(recipient, str) else {'recipient': recipient, 'sent_email': recipient.email}
        mail, created = self.get_or_create(sent=False, forced=forced, type=mail_type, **kwargs)
        # Ajouter des données au mail en file
        for item in mail_data:
            mail.set_data(item, mail_data[item] if mail.get_data(item) is None else mail.get_data(item) + mail_data[item])
        if created is True:
            mail.minimum_time = timezone.now() + datetime.timedelta(minutes=mail.type.interval)
        mail.save()

    @transaction.atomic
    def process(self, forced=False, bypass_delay=False):
        """
        Traiter la file d'attente et expédier des mails

        :param bypass_delay: envoyer les mails même si l'utilisateur a défini des limites empêchant d'envoyer maintenant
        :param forced: True, False ou 'all', définit le type d'emails à envoyer.
        :returns: le nombre d'emails effectivement envoyés
        """
        if forced == 'all':
            return self.process(forced=False, bypass_delay=bypass_delay) + self.process(forced=True, bypass_delay=bypass_delay)
        # Pas besoin de process si aucun mail à expédier
        if not self.filter(sent=False, discarded=False).exists():
            return 0
        # Adresse du sender (selon template+settings)
        sender = render_to_string('messaging/mail/layout/sender.txt', {'settings': settings}, default_context())
        # Supprimer les mails sans utilisateur et non importants
        self.orphans().delete()
        # Récupérer la liste des membres à qui envoyer un mail
        email_addresses = self.filter(sent=False, discarded=False).values_list('sent_email', flat=True).distinct()
        # Total de mails envoyés à calculer
        mail_counter = 0
        mail_ceiling = getattr(settings, 'MESSAGING_MAX_BATCH', 30)
        if len(email_addresses) > mail_ceiling * 8:
            mail_ceiling = len(email_addresses) / 2
        # Traiter un groupe de mails pour chacun des utilisateurs
        mails_to_send = []
        for email in email_addresses:
            # Ne traiter que si la configuration de l'utilisateur autorise
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                user = None
            if (user is None or user.can_send_mail() or bypass_delay or forced) and mail_counter < mail_ceiling:
                # Traiter les mails non marqués comme *forcés*
                mails = self.filter(sent_email=email, forced=forced, sent=False, discarded=False)
                # Envoyer chaque mail si son heure minimum d'envoi est atteinte
                for mail in mails:
                    if mail.can_send() or bypass_delay:
                        parts = mail.render()
                        mails_to_send.append([sender, email, one_line(parts['title']), parts['text'], parts['html']])
                        mail.sent = True
                        mail.sent_time = timezone.now()
                        mail.save()
                        mail_counter += 1
                if user:
                    user.reset_next_mail()
                # Et supprimer l'utilisateur de la file
                mails.update(sent=True)
        # L'envoi de mail peut durer longtemps. (timeout, NXDomain, etc.)
        # Si le serveur SQL timeoute avant le timeout DNS, il
        # sera impossible de mettre à jour la base de données. (server gone)
        # Ici, on envoie donc les mails après avoir mis à jour la base.
        for mail in mails_to_send:
            if self._send_mail(*mail) is False:
                mail_counter -= 1
        return mail_counter


class MailEvent(UUID128Model, DataModel):
    """ Événement mail """
    # Champs
    type = models.ForeignKey('messaging.MailType', related_name='events', verbose_name=_("Mail type"))
    queued = models.DateTimeField(default=timezone.now, verbose_name=_("Queue time"))
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='mailevents_to', verbose_name=_("Recipient"))
    forced = models.BooleanField(default=False, db_index=True, verbose_name=_("Force sending"))
    sent = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('mailevent', "Sent"))
    sent_time = models.DateTimeField(null=True, blank=True, default=None, verbose_name=_("Delivery time"))
    sent_email = models.CharField(max_length=96, default="", blank=True, verbose_name=_("Email used"))
    minimum_time = models.DateTimeField(default=timezone.now, verbose_name=_("Minimum delivery"))
    discarded = models.BooleanField(default=False, verbose_name=_("Discarded"))
    objects = MailEventManager()

    # Getter
    @addattr(boolean=True, short_description=_("Can be sent now"))
    def can_send(self):
        """ Renvoyer si cet événement peut être distribué """
        return (self.minimum_time <= timezone.now()) or self.forced

    @addattr(short_description=_("Delivery"))
    def get_delivery_delay(self):
        """ Renvoyer l'heure relative où l'envoi sera autorisé """
        return pretty.date(self.minimum_time)

    @addattr(allow_tags=True, short_description=_("Rendering"))
    def render(self):
        """ Renvoyer les informations de rendu de l'événement """
        template = 'messaging/mail/{name}.html'.format(name=self.type.template)
        data_set = {key: list(set(self.data[key])) for key in self.data}
        data_set.update({'event': self})
        title, text, html = [render_block_to_string(template, label, data_set) for label in ['title', 'text', 'html']]
        title = one_line(title)
        return {'title': title, 'text': text, 'html': render_to_string('messaging/mail/layout/html.html', {'html': html})}

    # Setter
    def postpone(self, minutes):
        """ Retarder l'événement de n minutes """
        self.minimum_time += datetime.timedelta(minutes=minutes)
        self.save(update_fields=['minimum_time'])

    # Métadonnées
    class Meta:
        verbose_name = _("mail event")
        verbose_name_plural = _("mail events")
        app_label = "messaging"
