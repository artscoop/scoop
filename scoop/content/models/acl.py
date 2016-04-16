# coding: utf-8

from autoslug.fields import AutoSlugField
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.content.acl import ACLModel
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
        elements = path.split('/', 6)
        if len(elements) >= 6:
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
    ACL_PATHS = {0: 'password'}
    PASSWORD = 0

    # Champs
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, verbose_name=_("Owner"))
    mode = models.PositiveSmallIntegerField(default=PASSWORD, verbose_name=_("Mode"))
    name = models.CharField(max_length=24, blank=False, verbose_name=_("Name"))
    slug = AutoSlugField(max_length=32, populate_from='name', unique_with=['uuid'], db_index=True, verbose_name=_("Slug"))
    password = models.CharField(max_length=128, blank=False, verbose_name=_("Password"))

    # Getter
    def get_acl_directory(self):
        """ Renvoyer le nom de répertoire d'ACL pour l'objet """
        return "{acl}/{spread}/{owner}/{name}".format(acl=self.ACL_PATHS[self.PASSWORD], name=self.get_slug(),
                                                      owner=self.owner.username, spread=ACLModel._get_hash_path(self.owner.username))

    def get_slug(self):
        """ Renvoyer le nom du répertoire ACL """
        return self.slug or 'default'

    def check_password(self, password):
        """ Renvoyer si un mot de passe correspond à cette configuration """
        return check_password(password)

    # Setter
    def set_password(self, password):
        """ Définit le mot de passe de la configuration ACL """
        self.password = make_password(password)

    # Métadonnées
    class Meta:
        verbose_name = _("ACL configuration")
        verbose_name_plural = _("ACL configurations")
        unique_together = [('owner', 'name')]
        index_together = [('mode', 'slug')]
        app_label = 'content'
