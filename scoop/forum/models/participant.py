# coding: utf-8
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.model.model import SingleDeleteManager


class ParticipantManager(SingleDeleteManager):
    """ Manager des destinataires """

    # Getter
    def get_thread_count(self, user, since=None, ghost=False):
        """ Renvoyer le nombre de fils pour le destinataire """
        filtering = {'active': True} if ghost is False else {}
        return self.filter(user=user, thread__started__gt=since, **filtering).count()

    def get_acknowledged_count(self, user):
        """ Renvoyer le nombre de fils dont un utilisateur a connaissance """
        return self.filter(user=user, acknowledged=True).count()

    def is_unread(self, thread, user):
        """
        Renvoyer si un utilisateur n'a pas lu un fil

        :param thread: fil de discussion
        :param user: utilisateur
        """
        return self.filter(thread=thread, user=user, unread=True).exists()

    # Setter
    def set_unread_by_message(self, message):
        """ Marquer comme non lu le fil du message pour tous les destinataires du message """
        for recipient in message.thread.get_recipients(exclude=message.author):
            self.set_unread(message.thread, recipient)
        self.set_read(message.thread, message.author)

    def set_unread(self, thread, user):
        """
        Marquer qu'un utilisateur n'a pas lu un fil

        :param user: utilisateur ou requête
        :type user: django.auth.models.User | django.http.HttpRequest
        """
        user = user if isinstance(user, get_user_model()) else user.user
        if thread.is_recipient(user):
            self.filter(thread=thread, user=user, unread=False).update(unread=True, unread_date=timezone.now())
            return True
        return False

    def set_all_read_for(self, user):
        """ Marquer tous les sujets comme lus pour un utilisateur """
        self.filter(user=user).update(unread=False, acknowledged=True)

    def set_read(self, thread, user=None):
        """ Marquer comme lu un sujet par un utilisateur """
        if thread:
            self.filter(thread=thread, unread=True, **({'user': user} if user else {})).update(unread=False, acknowledged=True, unread_date=timezone.now())

    def update_counter(self, user, thread):
        """ Mettre à jour le nombre de messages envoyés par un utilisateur dans un fil """
        try:
            recipient = self.get(user=user, thread=thread)
            recipient.counter = thread.get_user_message_count(user)
            recipient.save(update_fields=['counter'])
        except Participant.DoesNotExist:
            pass


class Participant(DatetimeModel, DataModel):
    """ Destinataire """

    # Constantes
    DATA_KEYS = ['is_important']

    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name="user_participant", on_delete=models.CASCADE, verbose_name=_("User"))
    thread = models.ForeignKey("forum.Thread", null=False, related_name='participants', on_delete=models.CASCADE, verbose_name=_("Thread"))
    active = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('participant', "Is active"))
    unread = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('thread', "Unread"))
    unread_date = models.DateTimeField(blank=True, null=True, default=None, verbose_name=pgettext_lazy('thread', "Unread time"))
    counter = models.PositiveIntegerField(default=0, db_index=True, verbose_name=_("Message count"))
    objects = ParticipantManager()

    # Setter
    def disable(self):
        """ Désactiver le destinataire dans le fil """
        if self.active is True:
            self.update(save=True, active=False)
            return True
        return False

    def enable(self):
        """ Réactiver le destinataire dans le fil """
        if self.active is False:
            self.update(save=True, active=True)
            return True
        return False

    def update_counter(self):
        """ Mettre à jour le nombre de messages envoyés dans le fil """
        self.counter = self.thread.get_user_message_count(self.user)
        self.save(update_fields=['counter'])

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "{name}".format(name=self.user.username)

    def get_absolute_url(self):
        """ Renvoyer l'URL de l'objet """
        return self.user.get_absolute_url()

    # Métadonnées
    class Meta:
        unique_together = (('thread', 'user'),)
        verbose_name = _("participant")
        verbose_name_plural = _("participants")
        app_label = "forum"
