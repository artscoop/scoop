# coding: utf-8
import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.data.textutil import one_line
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.django.templates import render_block_to_string
from scoop.core.util.model.model import SingleDeleteQuerySet
from scoop.core.util.stream.request import default_context
from scoop.messaging.util.signals import mailable_event


class AlertQuerySet(SingleDeleteQuerySet):
    """ Manager des alertes """

    # Getter
    def for_recipient(self, user):
        """ Renvoyer les alertes pour un utilisateur """
        return self.filter(recipient=user).order_by('-id')

    def read(self, user):
        """ Renvoyer les alertes lues par un utilisateur """
        return self.filter(recipient=user, read=True)

    def unread(self, user):
        """ Renvoyer les alertes non lues par un utilisateur """
        return self.filter(recipient=user, read=False)

    def get_unread_count(self, user):
        """ Renvoyer le nombre d'alertes non lues par un utilisateur """
        return self.filter(recipient=user, read=False).count()

    def by_level(self, level):
        """ Renvoyer les alertes pour un niveau d'importance """
        return self.filter(level=level)

    def read_since(self, minutes=1440):
        """ Renvoyer les alertes lues plus vieilles que n minutes """
        return self.filter(read=True, read_time__lt=timezone.now() - datetime.timedelta(minutes=minutes))

    # Setter
    def alert(self, recipients, mailtype_name, data, level=0, as_mail=None, **kwargs):
        """
        Envoyer une alerte à un ou plusieurs utilisateurs

        :param recipients: utilisateurs destinataires
        :param mailtype_name: nom de code du type de courrier/alerte à envoyer, :see: messaging.models.MailType
        :param data: dictionnaire d'infos pour le rendu de l'alerte/courrier
        :param level: niveau d'urgence de l'alerte
        :param as_mail: indique si un mail récapitulatif doit être envoyé. Par défaut None=n'envoie que les alertes de sécurité
        :returns: la liste des alertes effectivement envoyées
        :rtype: list<Alert>
        """
        from scoop.messaging.models.mailtype import MailType
        # Maximum de 1000 membres à qui envoyer l'alerte
        recipients = make_iterable(recipients)[0:1000]
        context = default_context()
        mailtype = MailType.objects.get_named(mailtype_name)
        template = 'messaging/alert/{name}.html'.format(name=mailtype.template)
        title, html = [render_block_to_string(template, label, data, context=context) for label in ['title', 'html']]
        as_mail = level == Alert.SECURITY if as_mail is None else as_mail
        alerts = []
        # Créer une alerte pour chacun des destinataires
        for recipient in recipients:
            new_alert = self.create(user=recipient, title=one_line(title), text=html, level=level)
            alerts.append(new_alert)
            if as_mail is True:
                mailable_event.send(sender=None, mailtype=mailtype_name, recipient=recipient, data=data)
        return alerts

    def alert_related(self, user, mailtype_name, data, level=0, as_mail=True, **kwargs):
        """ Envoyer une alerte aux utilisateurs ayant eu contact avec celui-ci """
        from scoop.messaging.models import Recipient
        recipients = Recipient.objects.related_users(user, ack=True)
        self.alert(recipients, mailtype_name, data, level, as_mail, **kwargs)


class Alert(DatetimeModel, DataModel):
    """ Alerte """

    # Constantes
    ALERT_LEVELS = [[0, _("Warning")], [1, _("Important")], [2, _("Security")]]
    WARNING, IMPORTANT, SECURITY = 0, 1, 2

    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='alerts_received', on_delete=models.CASCADE, verbose_name=_("User"))
    level = models.SmallIntegerField(default=0, choices=ALERT_LEVELS, validators=[MinValueValidator(0), MaxValueValidator(2)], verbose_name=_("Level"))
    title = models.CharField(max_length=80, blank=False, verbose_name=_("Title"))
    text = models.TextField(blank=False, verbose_name=_("Text"))
    items = models.CharField(max_length=160, default="", blank=True, verbose_name=_("Items"))
    read = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('alert', "Read"))
    read_time = models.DateTimeField(default=None, blank=True, null=True, db_index=True, verbose_name=pgettext_lazy('alert.time', "Read"))
    objects = AlertQuerySet.as_manager()

    # Getter
    def get_read(self):
        """ Renvoyer si l'alerte est lue """
        return self.read_time if self.read else None

    # Setter
    def do_read(self, user=None):
        """ Marquer l'alerte comme lue """
        if self.read_time is None and (user is None or user == self.user):
            self.read = True
            self.read_time = timezone.now()
            self.save(update_fields=['read', 'read_time'])
            return True
        return False

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("Alert for {user}").format(user=self.recipient)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        super(Alert, self).delete(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("alert")
        verbose_name_plural = _("alerts")
        ordering = ['-time']
        app_label = "messaging"
