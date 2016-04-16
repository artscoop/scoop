# coding: utf-8
import logging

from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID128Model
from scoop.core.util.data.textutil import text_to_list_of_lists
from scoop.messaging.util.signals import mailable_event
from scoop.user.util.signals import user_activated


logger = logging.getLogger(__name__)


class ActivationManager(models.Manager):
    """ Manager des activations utilisateur """

    # Getter
    def get_queryset(self):
        """ Renvoyer le queryset par défaut du manager """
        return super(ActivationManager, self).get_queryset()

    def get_user_from_uuid(self, uuid):
        """ Renvoyer l'utilisateur possédant une activation avec l'UUID désiré """
        from scoop.user.models import User
        # Renvoyer un utilisateur ou None
        user = User.objects.filter(activation__uuid=uuid)
        return user[0] if user.exists() else None

    # Actions
    def activate(self, uuid, username, request=None):
        """ Tenter d'activer un utilisateur via des informations d'activation """
        try:
            criteria = {'uuid': uuid} if uuid is not None else {}
            item = self.get(user__username__iexact=username, active=True, **criteria)
        except Activation.DoesNotExist:
            item = None
        # Puis activer l'utilisateur et désactiver l'activation
        if item is not None:
            item.user.set_active()
            if item.active is True:
                item.active = False
                item.update_uuid(save=False)
                item.save()
                user_activated.send(sender=item, user=item.user, request=request, failed=False)
                return True
        user_activated.send(sender=item, user=None, request=request, failed=True)
        return False

    def deactivate(self, user, admin=False):
        """ Désactiver un utilisateur """
        user.activation.active = not admin
        user.set_inactive()
        user.activation.save()

    def fix(self):
        """ Réparer les activations toujours actives pour un utilisateur actif """
        self.filter(user__is_active=True, active=True).update(active=False)


class Activation(DatetimeModel, UUID128Model):
    """ Activation ou réactivation utilisateur """

    # Constantes
    MAX_RESENDS = 5  # Maximum de renvois de mails de confirmation

    # Champs
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activation', primary_key=True, verbose_name=_("User"))
    # Dans le cas où l'email est indisponible, utiliser question secrète
    question = models.IntegerField(null=True, verbose_name=_("Secret question"))
    answer = models.CharField(max_length=96, blank=True, verbose_name=_("Answer"))
    # Activation possible ?
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('activation', "Active"))
    updates = models.SmallIntegerField(default=0, verbose_name=_("Updates"))
    resends = models.SmallIntegerField(default=0, verbose_name=_("Mail send count"))
    last_resend = models.DateTimeField(default=None, null=True, verbose_name=_(u"Mail sent"))
    details = models.CharField(max_length=48, default="", blank=True, verbose_name=_("Admin details"))
    objects = ActivationManager()

    # Getter
    def is_answer_ok(self, phrase):
        """ Renvoyer si une expression correspond à la réponse secrète """
        return phrase.lower().strip() == self.answer.lower().strip()

    def is_valid(self):
        """ Renvoyer si l'état de la validation est cohérent """
        return not (self.active and self.user.is_active)

    def can_be_sent(self):
        """ Renvoyer si le mail de validation peut être à nouveau envoyé """
        return self.resends < Activation.MAX_RESENDS and self.active and not self.user.is_active

    # Setter
    def update_uuid(self, save=True):
        """ Modifier l'UUID de l'activation """
        self.uuid = ""
        self.updates += 1
        self.resends = 0
        if save:
            self.save(update_fields=['uuid', 'updates'])

    # Actions
    def send_mail(self):
        """ Mettre en file rapide le courrier d'activation de l'utilisateur """
        if self.can_be_sent():
            from scoop.messaging.models import MailType
            # Envoyer un mail si le site est configuré correctement
            try:
                mailable_event.send(None, mailtype='user.activation', recipient=self.user, data={'activation': self})
                self.resends += 1
                self.last_resend = timezone.now()
                self.save(update_fields=['resends', 'last_resend'])
                return True
            except MailType.DoesNotExist:
                logger.warning("Cannot send activation info, mail type is not configured yet.")
        else:
            logger.warning("Cannot send activation info anymore for {user}: limit exceeded".format(user=self.user))
        return False

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{username}'s activation data").format(username=self.user.username)

    def __repr__(self):
        """ Renvoyer la représentation texte de l'objet """
        return unidecode(self.__str__())

    def __init__(self, *args, **kwargs):
        """ Initialiser l'objet """
        self._meta.get_field('question')._choices = text_to_list_of_lists(render_to_string("user/data/activate-question-choices.txt"), evaluate=False)
        super(Activation, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Activation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("user activation")
        verbose_name_plural = _("user activations")
        app_label = "user"
