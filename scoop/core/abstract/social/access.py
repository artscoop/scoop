# coding: utf-8
from django.apps.registry import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _


class PrivacyModel(models.Model):
    """ Mixin de modèle avec contrôle d'accès """

    # Constantes
    ACCESS_TYPES = [[0, _("Public")], [1, _("Friends")], [2, _("Personal")], [3, _("Friend groups")], [4, _("Registered users")]]
    PUBLIC, FRIENDS, PERSONAL, GROUPS, REGISTERED = 0, 1, 2, 3, 4

    if apps.is_installed('scoop.user.social'):

        # Champs
        access = models.SmallIntegerField(choices=ACCESS_TYPES, default=0, db_index=True, verbose_name=_("Access"))
        group_grants = GenericRelation('social.FriendGroupGrant', related_name="%(class)s_group_grants") if apps.is_installed('scoop.user.social') else None

        # Getter
        def _is_user_granted_in_group_grants(self, user):
            """ Renvoyer si un utilisateur fait partie des groupes autorisés """
            if self.group_grants is not None:
                for grant in self.group_grants.all():
                    if grant.group.has_member(user):
                        return True
            return False

        def is_accessible(self, user):
            """ Renvoyer si un utilisateur a accès au contenu """
            if user.has_perm('content.can_access_all_content'):
                return True
            elif self.access == PrivacyModel.PUBLIC:  # Public
                return True
            elif self.access == PrivacyModel.FRIENDS:  # Ami avec l'auteur
                from scoop.user.social.models import FriendList
                # C'est un succès si une amitié existe
                if FriendList.objects.exists(user, self.author):
                    return True
            elif self.access == PrivacyModel.PERSONAL and user == self.author:  # Seulement moi
                return True
            elif self.access == PrivacyModel.GROUPS:  # Dans un groupe d'amis autorisé
                return self._is_user_granted_in_group_grants(user)
            elif self.access == PrivacyModel.REGISTERED:  # Membres connectés
                return user.is_authenticated()
            return False

    # Métadonnées
    class Meta:
        abstract = True


class AccessLevelModel(models.Model):
    """ Mixin de modèle avec Niveau d'accès requis """

    # Constantes
    LEVEL_TYPES = [[0, _("Public")], [1, _("Members only")], [2, _("Staff only")]]
    PUBLIC, REGISTERED, STAFF = 0, 1, 2

    # Champs
    access_level = models.SmallIntegerField(choices=LEVEL_TYPES, default=0, db_index=True, verbose_name=_("Access level"))

    # Getter
    def is_accessible(self, user):
        """ Renvoyer si un utilisateur a accèss au contenu """
        if self.access_level == AccessLevelModel.PUBLIC:  # Public
            return True
        elif self.access_level == AccessLevelModel.REGISTERED:  # Authentifié
            return user.is_authenticated()
        elif self.access_level == AccessLevelModel.STAFF:  # Staff
            return user.is_staff
        return False

    # Métadonnées
    class Meta:
        abstract = True
