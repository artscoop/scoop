# coding: utf-8
from django.apps.registry import apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.data import DataModel


class PrivacyModel(models.Model):
    """ Mixin de modèle avec contrôle d'accès """

    # Constantes
    ACCESS_TYPES = [[0, _("Public")], [1, _("Friends")], [2, _("Personal")], [3, _("Friend groups")], [4, _("Registered users")]]
    PUBLIC, FRIENDS, PERSONAL, CUSTOM, REGISTERED = 0, 1, 2, 3, 4

    if apps.is_installed('scoop.user.social'):

        # Champs
        access = models.SmallIntegerField(choices=ACCESS_TYPES, default=0, db_index=True, verbose_name=_("Access"))

        # Getter
        def is_user_granted_custom(self, user):
            """ Renvoyer si un utilisateur fait partie des utilisateurs/groupes autorisés """
            from scoop.user.social.models import FriendGroup
            grants = self.get_data('privacy')
            users = grants.get('users', [])
            groups = grants.get('groups', [])
            # Si l'utilisateur lui-même est répertorié, c'est bon
            if user.pk in users:
                return True
            # Si l'un des groupes d'amis répertoriés contient l'utilisateur, c'est bon
            for grant in FriendGroup.objects.filter(pk__in=groups):
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
            elif self.access == PrivacyModel.REGISTERED:  # Membres connectés
                return user.is_authenticated()
            elif self.access == PrivacyModel.CUSTOM:  # Dans un groupe d'amis autorisé
                return self.is_user_granted_custom(user)
            return False

        # Setter
        def set_user_grants(self, users):
            """ Définir les utilisateurs autorisés à afficher le contenu """
            grants = self.get_data('privacy')
            grants['users'] = [user.pk for user in users]
            self.set_data('privacy', grants, save=True)

        def set_group_grants(self, groups):
            """ Définir les groupes autorisés à afficher le contenu """
            grants = self.get_data('privacy')
            grants['groups'] = [group.pk for group in groups]
            self.set_data('privacy', grants, save=True)

        def reset_custom_grants(self):
            """ Réinitialiser les autorisations d'accès particulières """
            self.set_data('privacy', dict(), save=True)

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
