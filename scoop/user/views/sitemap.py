# coding: utf-8
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from scoop.user.models.user import User


class ProfileSitemap(Sitemap):
    """ Sitemap des profils utilisateurs """
    limit = getattr(settings, 'SITEMAPS_ITEMS_PER_PAGE', 10000)

    # Getter
    def items(self):
        """ Renvoyer les objets du sitemap """
        return User.objects.only('id', 'username').active()

    def location(self, obj):
        """ Renvoyer l'URL d'un profil du sitemap """
        return obj.get_absolute_url()
