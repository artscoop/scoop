# coding: utf-8
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.model.model import SingleDeleteManager
from scoop.messaging.models.negotiation import Negotiation


class QuotaManager(SingleDeleteManager):
    """ Manager des quotas """

    # Getter
    def get_threads_today_by(self, user):
        """ Renvoyer le nombre de fils créés aujourd'hui par un utilisateur """
        today = timezone.now().date()
        count = user.threads.filter(started__gte=today).count()
        return count

    def get_negotiations_today_by(self, user):
        """ Renvoyer le nombre de négociations envoyées aujourd'hui par un utilisateur """
        timestamp = Negotiation.get_timestamp(timezone.now().date())
        count = user.negotiations_made.filter(time__gte=timestamp).count()
        return count

    def get_messages_today_by(self, user):
        """ Renvoyer le nombre de messages postés aujourd'hui par un utilisateur """
        from scoop.messaging.models import Message
        # Calculer la date d'aujourd'hui minuit
        timestamp = Message.get_timestamp(timezone.now().date())
        count = user.messages_sent.filter(time__gte=timestamp).count()
        return count

    def exceeded_threads_for(self, user):
        """ Renvoyer si le quota est atteint pour un utilisateur """
        if user.has_perm('messaging.unlimited_threads') or user.has_perm('messaging.unlimited_messages'):
            return False
        # Retrouver le quota maximum parmi les groupes de l'utilisateur
        quota = max([getattr(getattr(group, 'quota', None), 'max_threads', 0) for group in
                     user.groups]) if user.groups.exists() else settings.MESSAGING_DEFAULT_THREAD_QUOTA
        # Effectuer le calcul le reste du temps
        thread_count = self.get_threads_today_by(user)
        return thread_count > quota

    def exceeded_negotiations_for(self, user):
        """ Renvoyer si le quota est atteint pour un utilisateur """
        if user.has_perm('messaging.unlimited_negotiations') or user.has_perm('messaging.unlimited_messages'):
            return False
        # Retrouver le quota maximum parmi les groupes de l'utilisateur
        quota = max([getattr(getattr(group, 'quota', None), 'max_negotiations', 0) for group in
                     user.groups]) if user.groups.exists() else settings.MESSAGING_DEFAULT_NEGOTIATION_QUOTA
        # Effectuer le calcul le reste du temps
        negotiation_count = self.get_negotiations_today_by(user)
        return negotiation_count > quota


class Quota(models.Model):
    """ Quota de messages """

    # Champs
    group = models.OneToOneField('auth.Group', null=False, primary_key=True, related_name='message_quota', on_delete=models.CASCADE, verbose_name=_("Group"))
    max_threads = models.IntegerField(default=getattr(settings, 'MESSAGING_DEFAULT_THREAD_QUOTA', 32), verbose_name=_("Max threads/day"))
    max_negotiations = models.IntegerField(default=getattr(settings, 'MESSAGING_DEFAULT_NEGOTIATION_QUOTA', 32), verbose_name=_("Max negotiations/day"))
    objects = QuotaManager()

    # Overrides
    def __str__(self):
        """ Renvoyer la version texte de l'objet """
        return "Messaging quota for group {group}".format(self.group.name)

    # Métadonnées
    class Meta:
        verbose_name = _("message quota")
        verbose_name_plural = _("message quotas")
        permissions = (("unlimited_threads", "Can overstep thread quotas"),
                       ("unlimited_messages", "Can overstep message quotas"),
                       )
        app_label = "messaging"
