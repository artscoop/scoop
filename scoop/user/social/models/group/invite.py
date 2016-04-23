# coding: utf-8
from django.conf import settings
from django.db import models
from django.db.utils import ProgrammingError
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
        except ProgrammingError:
            return False


class Invite(AuthoredModel, DatetimeModel, GenericModel):
    """ Invitation à un contenu "invitable" """

    # Constantes
    STATUSES = [[0, _("Pending")], [1, _("Accepted")], [2, _("Denied")], [3, _("Permanently denied")]]
    PENDING, ACCEPTED, DENIED, NUKED = 0, 1, 2, 3

    # Champs
    target = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name="invite_targeted", verbose_name=_("Target"))
    status = models.SmallIntegerField(choices=STATUSES, default=0, verbose_name=_("Status"))

    # Getter
    def is_denied(self):
        """ Renvoyer si une invitation est refusée """
        return self.status in [Invite.DENIED, Invite.NUKED]

    # Setter
    def accept(self):
        """ Accepter l'invitation """
        if self.status != Invite.ACCEPTED:
            invite_accepted.send(sender=self.content_object._meta.concrete_model, instance=self)
            self.status = Invite.ACCEPTED
            self.save(update_fields=['status'])
            return True
        return False

    def deny(self, permanent=False):
        """ Refuser l'invitation """
        if self.status != (Invite.NUKED if permanent else Invite.DENIED):
            invite_denied.send(sender=self.content_object._meta.concrete_model, instance=self)
            self.status = Invite.DENIED if not permanent else Invite.NUKED
            self.save(update_fields=['status'])
            return True
        return False

    def cancel(self):
        """ Annuler l'invitation """
        self.delete()

    # Métadonnées
    class Meta:
        unique_together = [['content_type', 'object_id', 'target']]
        verbose_name = _("Group invite")
        verbose_name_plural = _("Group invites")
        app_label = "social"
