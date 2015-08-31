# coding: utf-8
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.generic import GenericModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.user.social.util.signals import invite_accepted, invite_denied


class InviteManager(SingleDeleteManager):
    """ Manager des invitations"""

    # Setter
    def add(self, content, user):
        """ Créer une invitation à une cible """
        try:
            if getattr(content, 'is_invite_content', lambda: False)():
                invite = Invite(content_object=content, target=user)
                invite.save()
                return True
        except:
            return False


class Invite(AuthoredModel, DatetimeModel, GenericModel):
    """ Invitation à un contenu "invitable" """
    # Constantes
    STATUSES = [[0, _("Pending")], [1, _("Accepted")], [2, _("Denied")], [3, _("Permanently denied")]]
    # Champs
    target = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name="invite_targeted", verbose_name=_("Target"))
    status = models.SmallIntegerField(choices=STATUSES, default=0, verbose_name=_("Status"))

    # Getter
    def is_denied(self):
        """ Renvoyer si une invitation est refusée """
        return self.status in [2, 3]

    # Setter
    def accept(self):
        """ Accepter l'invitation """
        invite_accepted.send(sender=self.content_object._meta.concrete_model, instance=self)
        self.status = 1
        self.save(update_fields=['status'])

    def deny(self, permanent=False):
        """ Refuser l'invitation """
        invite_denied.send(sender=self.content_object._meta.concrete_model, instance=self)
        self.status = 2 if not permanent else 3
        self.save(update_fields=['status'])

    def cancel(self):
        """ Annuler l'invitation """
        self.delete()

    # Métadonnées
    class Meta:
        unique_together = (('content_type', 'object_id', 'target'),)
        verbose_name = _("Group invite")
        verbose_name_plural = _("Group invites")
        app_label = "social"
