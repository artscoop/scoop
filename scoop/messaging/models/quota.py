# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.model.model import SingleDeleteManager


class QuotaManager(SingleDeleteManager):
    """ Manager des quotas """

    # Getter
    def get_threads_today_by(self, user):
        """ Renvoyer le nombre de fils créés aujourd'hui par un utilisateur """
        today = timezone.now().date()
        count = user.threads.filter(started__gte=today).count()
        return count

    def get_messages_today_by(self, user):
        """ Renvoyer le nombre de messages postés aujourd'hui par un utilisateur """
        from scoop.messaging.models import Message
        # Calculer la date d'aujourd'hui minuit
        timestamp = Message.get_timestamp(timezone.now().date())
        count = user.messages_sent.filter(time__gte=timestamp).count()
        return count

    def exceeded_for(self, user):
        """ Renvoyer si le quota est atteint pour un utilisateur """
        if user.has_perm('messaging.unlimited_threads') or user.has_perm('messaging.unlimited_messages'):
            return False
        # Retrouver le quota maximum parmi les groupes de l'utilisateur
        quota = max([getattr(getattr(group, 'quota', None), 'max_threads', 0) for group in user.groups]) if user.groups.exists() else settings.MESSAGING_DEFAULT_THREAD_QUOTA
        # Effectuer le calcul le reste du temps
        thread_count = self.get_threads_today_by(user)
        return thread_count > quota


class Quota(models.Model):
    """ Quota de messages """
    group = models.OneToOneField('auth.Group', null=False, primary_key=True, related_name='message_quota', on_delete=models.CASCADE, verbose_name=_(u"Group"))
    max_threads = models.SmallIntegerField(default=getattr(settings, 'MESSAGING_DEFAULT_THREAD_QUOTA', 32), verbose_name=_(u"Max threads/day"))
    objects = QuotaManager()

    # Métadonnées
    class Meta:
        verbose_name = _(u"message quota")
        verbose_name_plural = _(u"message quotas")
        permissions = (("unlimited_threads", u"Can overstep thread quotas"),
                       ("unlimited_messages", u"Can overstep message quotas"),
                       )
        app_label = "messaging"
