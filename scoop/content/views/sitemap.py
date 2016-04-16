# coding: utf-8
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from scoop.content.models.content import Content
from scoop.core.util.data.dateutil import is_new


class ContentSitemap(Sitemap):
    """ Sitemap des contenus """
    limit = getattr(settings, 'SITEMAPS_ITEMS_PER_PAGE', 50000)

    # Getter
    def items(self):
        """ Renvoyer la liste des éléments du sitemap """
        return Content.objects.visible().only('updated', 'id', 'slug')

    def lastmod(self, obj):
        """ Renvoyer la date de mise à jour d'un contenu """
        return obj.updated

    def location(self, obj):
        """ Renvoyer l'URL d'un contenu """
        return obj.get_absolute_url()

    def changefreq(self, obj):
        """ Renvoyer la fréquence de modification du contenu """
        return is_new(obj.updated, 7) and 'hourly' or 'weekly'
