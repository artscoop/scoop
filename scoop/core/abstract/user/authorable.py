# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AuthorableModel(models.Model):
    """ Objet pouvant avoir un auteur """
    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name=_("Author"))

    # Métadonnées
    class Meta:
        abstract = True
