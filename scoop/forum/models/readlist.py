# coding: utf-8
from annoying.fields import AutoOneToOneField
from autofixture.constraints import unique_together_constraint
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.data import DataModel


class ReadList(DataModel):
    """
    TODO: Liste de contenus lus
    """

    # Constantes
    DATA_KEYS = ['read']

    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='readlist', on_delete=models.CASCADE, verbose_name=_("User"))
    category = models.ForeignKey('content.Category', related_name='+', on_delete=models.CASCADE, verbose_name=_("Category"))

    # Setter
    def read(self, user):
        """ Readr un utilisateur """
        if user.is_authenticated():
            read = self.get_data('read', set())
            read.add(user.id)
            self.set_data('read', read, True)

    def unread(self, user, by_id=False):
        """ Ne plus readr un utilisateur """
        users = user if isinstance(user, [list, tuple, set]) else [user]
        read = self.get_data('read') or set()
        for user in users:
            read.discard(user if by_id else user.id)
        self.set_data('read', read, True)

    def reset(self):
        """ Remettre à zéro la liste des ignorés """
        self.set_data('read', set(), True)

    # Getter
    def is_read(self, user):
        """ Renvoyer si un utilisateur est ignoré """
        return user.id in (self.get_data('read') or set())

    def get_read_users(self):
        """ Renvoyer les utilisateurs ignorés """
        user_ids = list(self.get_data('read') or set())
        users = get_user_model().objects.filter(pk__in=user_ids)
        return users

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(ReadList, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("read list")
        verbose_name_plural = _("read lists")
        unique_together = [['user', 'category']]
        app_label = "forum"
