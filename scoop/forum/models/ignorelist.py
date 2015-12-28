# coding: utf-8
from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.data import DataModel


class IgnoreList(DataModel):
    """ Liste de personnes ignorées """
    # Constantes
    DATA_KEYS = ['ignored']
    # Champs
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, null=True, related_name='forum_ignorelist', on_delete=models.CASCADE, verbose_name=_("User"))

    # Setter
    def ignore(self, user):
        """ Ignorer un utilisateur """
        if user.is_authenticated():
            ignored = self.get_data('ignored', set())
            ignored.add(user.id)
            self.set_data('ignored', ignored, True)

    def unignore(self, user, by_id=False):
        """ Ne plus ignorer un utilisateur """
        users = user if isinstance(user, [list, tuple, set]) else [user]
        ignored = self.get_data('ignored') or set()
        for user in users:
            ignored.discard(user if by_id else user.id)
        self.set_data('ignored', ignored, True)

    def reset(self):
        """ Remettre à zéro la liste des ignorés """
        self.set_data('ignored', set(), True)

    # Getter
    def is_ignored(self, user):
        """ Renvoyer si un utilisateur est ignoré """
        return user.id in (self.get_data('ignored') or set())

    def get_ignored_users(self):
        """ Renvoyer les utilisateurs ignorés """
        user_ids = list(self.get_data('ignored') or set())
        users = get_user_model().objects.filter(pk__in=user_ids)
        return users

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(IgnoreList, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("ignore list")
        verbose_name_plural = _("ignore lists")
        app_label = "forum"
