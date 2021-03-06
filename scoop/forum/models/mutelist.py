# coding: utf-8
from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.data import DataModel
from scoop.core.util.model.model import SingleDeleteManager


class MutelistManager(SingleDeleteManager):
    """ Manager de listes de blocage """

    # Getter
    def get_by_user(self, user):
        """ Renvoyer l'objet blocklist pour un utilisateur """
        return self.get_or_create(user=user)[0] if user is not None else self.get_global()


class Mutelist(DataModel):
    """ Liste de personnes ignorées """

    # Constantes
    DATA_KEYS = ['muted']

    # Champs
    objects = MutelistManager()
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, null=True, primary_key=False, related_name='forum_mutelist', on_delete=models.CASCADE,
                             verbose_name=_("User"))

    # Setter
    def mute(self, user):
        """ Muter un utilisateur """
        if user.is_authenticated():
            muted = self.get_data('muted', set())
            muted.add(user.id)
            self.set_data('muted', muted, True)

    def unmute(self, user):
        """
        Ne plus muter un utilisateur

        :param user: utilisateur à retirer de la liste des muets
        """
        users = user if isinstance(user, [list, tuple, set]) else [user]
        muted = self.get_data('muted') or set()
        for user in users:
            muted.discard(user.id if hasattr(user, 'id') else user)
        self.set_data('muted', muted, True)

    def reset(self, save=True):
        """ Remettre à zéro la liste des ignorés """
        self.set_data('muted', set(), save=save)

    # Getter
    def is_muted(self, user):
        """ Renvoyer si un utilisateur est ignoré """
        if user is not None:
            return user.id in (self.get_data('muted') or set())
        return False

    def get_muted_users(self):
        """ Renvoyer les utilisateurs ignorés """
        user_ids = list(self.get_data('muted') or set())
        users = get_user_model().objects.filter(pk__in=user_ids)
        return users

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Mutelist, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("mute list")
        verbose_name_plural = _("mute lists")
        app_label = "forum"
