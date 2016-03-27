# coding: utf-8

from autoslug.fields import AutoSlugField
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.uuid import UUID64Model


class CustomACLQuerySet(models.QuerySet):
    """ Queryset des ACL custom """

    # Getter
    def get_from_resource(self, path):
        """
        Renvoyer le custom ACL pour la ressource

        :type path: str
        :returns: un objet ACL pour la resource, ou None
        """
        elements = path.split('/')
        if len(elements) > 3:
            if elements[0] == 'password':
                owner = elements[1]
                slug = elements[2]
                acls = self.filter(owner__username=owner, mode=0, slug=slug)
                if acls.exists():
                    return acls.first()
        return None


class CustomACL(UUID64Model):
    """ Configuration personnalisée d'ACL """

    # Constantes
    ACL_CUSTOM_MODES = [(0, _("Password"))]
    PASSWORD = 0
    ACL_PATHS = {0: 'password'}

    # Champs
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, verbose_name=_("Owner"))
    mode = models.PositiveSmallIntegerField(default=PASSWORD, verbose_name=_("Mode"))
    name = models.CharField(max_length=24, blank=False, verbose_name=_("Name"))
    slug = AutoSlugField(max_length=32, populate_from='name', unique_with=('uuid',), verbose_name=_("Slug"))
    password = models.CharField(max_length=128, blank=False, verbose_name=_("Password"))

    # Getter
    def get_acl_directory(self):
        """" Renvoyer le nom de répertoire d'ACL pour l'objet """
        return "{acl}/{owner}/{name}".format(acl=self.ACL_PATHS[self.PASSWORD], owner=self.owner.username, name=self.get_slug())

    def get_slug(self):
        """ Renvoyer le nom du répertoire ACL """
        return self.slug or 'default'

    # Métadonnées
    class Meta:
        verbose_name = _("ACL configuration")
        verbose_name_plural = _("ACL configurations")
        unique_together = [('owner', 'name')]
        app_label = 'content'
