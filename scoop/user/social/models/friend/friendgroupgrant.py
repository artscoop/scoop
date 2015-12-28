# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.generic import GenericModel
from scoop.core.util.model.model import SingleDeleteManager


class FriendGroupGrantManager(SingleDeleteManager):
    """ Manager des autorisations à groupes d'amis """

    # Getter
    def is_granted(self, user, target):
        """ Renvoyer si un utilisateur est autorisé sur une cible """
        criteria = FriendGroupGrant.get_object_dict(target)
        return any([grant.is_granted(user) for grant in self.filter(**criteria)])


class FriendGroupGrant(GenericModel):
    """ Permission d'accès à un groupe d'amis """
    # Champs
    group = models.ForeignKey('social.FriendGroup', related_name='grants', verbose_name=_("Group"))
    objects = FriendGroupGrantManager()

    # Getter
    def is_granted(self, user):
        """ Renvoyer si cette permission concerne un utilisateur """
        return self.group.has_member(user)

    # Métadonnées
    class Meta(object):
        verbose_name = _("friend group grant")
        verbose_name_plural = _("friend group grants")
        app_label = "social"
