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
            if elements[0] == CustomACL.ACL_PATHS[CustomACL.PASSWORD]:
                owner = elements[1]
                slug = elements[2]
                acls = self.filter(owner__username=owner, mode=0, slug=slug)
                if acls.exists():
                    return acls.first()
        return None


class CustomACL(UUID64Model):
    """
    Configuration personnalisée d'ACL

    Comment fonctionnent les configurations personnalisées d'ACL ?
    Une instance de modèle ACL possède plusieurs modes d'ACL de base,
    entre Public, Authentifié, Privé et Social. Un mode supplémentaire,
    Personnalisé, permet à l'heure actuelle de définir des mots de passe.
    Vous pouvez assigner plusieurs contenus ACL au même mot de passe,
    et mélanger les modes ACL arbitrairement sur l'ensemble de vos contenus.
    """

    # Constantes
    ACL_CUSTOM_MODES = [(0, _("Password"))]
    ACL_PATHS = {0: 'password'}
    PASSWORD = 0

    # Champs
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, verbose_name=_("Owner"))
    mode = models.PositiveSmallIntegerField(default=PASSWORD, choices=ACL_CUSTOM_MODES, verbose_name=_("Mode"))
    name = models.CharField(max_length=24, blank=False, verbose_name=_("Name"))
    slug = AutoSlugField(max_length=32, populate_from='name', unique_with=['uuid'], db_index=True, verbose_name=_("Slug"))
    password = models.CharField(max_length=128, blank=False, verbose_name=_("Password"))
    objects = CustomACLQuerySet.as_manager()

    # Getter
    def get_acl_directory(self):
        """ Renvoyer le nom de répertoire d'ACL pour l'objet """
        return "{acl}/{spread}/{owner}/{name}".format(acl=self.ACL_PATHS[int(self.mode)], name=self.get_slug(),
                                                      owner=self.owner.username, spread=ACLModel._get_hash_path(self.owner.username))

    def get_slug(self):
        """ Renvoyer le nom du répertoire ACL """
        return self.slug or 'default'

    def check_password(self, password):
        """
        Renvoyer si un mot de passe est valide pour cette configuration d'ACL

        :param password: mot de passe
        :returns: True si le mot de passe est valide, False sinon
        :rtype: bool
        """
        return check_password(password, self.password)

    def is_valid(self, request):
        """
        Renvoyer si l'utilisateur connecté a accès au contenu

        :param request: objet HttpRequest
        :rtype: bool
        """
        session_key = self._get_session_key()
        if session_key in request.session:
            return self.check_password(request.session[session_key])
        return False

    # Privé
    def _get_session_key(self):
        """ Renvoyer le nom de clé de session utilisé pour vérifier le mot de passe """
        session_key = "acl-{uuid}".format(uuid=self.uuid)
        return session_key

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
