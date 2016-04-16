# coding: utf-8
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.data import DataModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


class FriendGroupManager(SingleDeleteManager):
    """ Manager des groupes d'amis """

    # Getter
    def for_user(self, user):
        return self.filter(user=user)


class FriendGroup(DataModel):
    """ Groupe personnalisé d'amis """

    # Constantes
    GROUP_NAMES = [[item, item] for item in [_("Family"), _("Friends"), _("Colleagues"), _("Acquaitances"), _("Friends 2"), _("Friends 3")]]

    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendgroups', verbose_name=_("User"))
    name = models.CharField(max_length=24, choices=GROUP_NAMES, blank=False, verbose_name=_('Name'))
    objects = FriendGroupManager()

    # Getter
    def has_member(self, friend):
        """ Renvoyer si un utilisateur fait partie du groupe """
        return friend.pk in self.get_data('friends')

    def get_members(self):
        """ Générer la liste des utilisateurs du groupe """
        purge = []
        users = get_user_model().objects.filter(id__in=self.get_data('friends'))
        for user in users:
            if self.user.friends.is_friend(user):
                yield user
            else:
                purge.append(user)
        if purge:
            self.remove(purge)

    @addattr(short_description=_("Friend count"))
    def get_friend_count(self):
        """ Renvoyer le nombre d'amis dans le groupe """
        return len(self.get_data('friends'))

    # Setter
    def add(self, friends):
        """ Ajouter une liste d'amis à un groupe """
        friendlist = self.get_data('friends')
        new_friends = [friend for friend in friends if friend.pk not in friendlist]
        if new_friends:
            friends = self.get_data('friends')
            for friend in new_friends:
                friends.append(friend.pk)
            self.set_data('friends', friends)
            return True
        return False

    def remove(self, friends):
        """ Supprimer un ou plusieurs amis d'un groupe """
        old_friends = [friend for friend in friends if self.has_member(friend)]
        if old_friends:
            friends = self.get_data('friends')
            remaining_friends = [friend for friend in friends if friend not in old_friends]
            self.set_data('friends', remaining_friends)
            return True
        return False

    # Métadonnées
    class Meta(object):
        verbose_name = _("friend group")
        verbose_name_plural = _("friend groups")
        unique_together = (('user', 'name',),)
        app_label = "social"
