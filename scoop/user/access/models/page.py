# coding: utf-8
from __future__ import absolute_import

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


class PageManager(models.Manager):
    """ Manager des pages """

    # Getter
    def get_page(self, path):
        """ Renvoyer l'objet Page à une URL """
        if path.endswith('/'):
            path = path[:-1]  # Supprimer le slash final
        try:
            page = self.get(path__iexact=path)
        except:
            page = Page(path=path)
            page.save()
        return page


class Page(models.Model):
    """ Page du site """
    # Champs
    path = models.CharField(max_length=192, blank=False, db_index=True, unique=True, verbose_name=_("Path"))
    objects = PageManager()

    # Getter
    def get_visitors(self, limit=None):
        """ Renvoyer les utilisateurs ayant visité la page """
        visitors = get_user_model().objects.filter(access__page=self).distinct()
        return visitors if limit is None else visitors[:limit]

    # Overrides
    def get_absolute_url(self):
        """ Renvoyer l'URL de la page """
        return self.path

    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.path

    class Meta:
        """ Métadonnées """
        verbose_name = _("site page")
        verbose_name_plural = _("site pages")
        app_label = 'access'
