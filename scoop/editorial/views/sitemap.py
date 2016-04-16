# coding: utf-8
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from scoop.editorial.models.page import Page


class EditorialSitemap(Sitemap):
    """ Sitemap des pages """
    changefreq = 'weekly'
    priority = 0.5
    limit = getattr(settings, 'SITEMAPS_ITEMS_PER_PAGE', 50000)

    # Getter
    def items(self):
        """ Renvoyer les éléments du sitemap """
        return Page.objects.filter(active=True, anonymous=True)

    def lastmod(self, obj):
        """ Renvoyer la dernière modification de l'élément du sitemap """
        return obj.datetime

    def location(self, obj):
        """ Renvoyer l'URL de la page """
        return obj.get_absolute_url()

    def changefreq(self, obj):
        """ Renvoyer la fréquence de modification de la page """
        # Renvoyer hourly si le contenu a été modifié récemment
        return 'weekly'
