# coding: utf-8
import logging
from datetime import datetime, timedelta

from django.contrib.contenttypes import fields
from django.db import models
from django.http.response import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.generic import GenericModelMixin
from scoop.core.util.model.model import SingleDeleteManager

logger = logging.getLogger(__name__)


class RedirectionManager(SingleDeleteManager):
    """ Manager des redirections """

    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(RedirectionManager, self).get_queryset()

    # Getter
    def at_path(self, path):
        """ Renvoyer la redirection active pour une URL """
        try:
            path = path.rstrip('/')
            return self.get(base=path, active=True)
        except Redirection.DoesNotExist:
            return None

    def get_expired(self):
        """ Renvoyer les redirections expirées """
        return self.filter(active=True, expires__lt=datetime.now())

    # Setter
    def record(self, base, destination):
        """ Enregistrer une nouvelle redirection """
        if hasattr(destination, 'get_absolute_url'):
            redirection = Redirection(base=base)
            redirection.content_object = destination
            redirection.save()
            return True
        return False


class Redirection(GenericModelMixin, DatetimeModel):
    """ Redirection d'URL """
    active = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('redirection', u"Active"))
    base = models.CharField(max_length=250, unique=True, blank=False, verbose_name=_(u"Original URL"))
    expires = models.DateTimeField(default=datetime.now() + timedelta(days=3650), verbose_name=_(u"Expiry"))  # 10 ans après démarrage du serveur
    permanent = models.BooleanField(default=True, verbose_name=pgettext_lazy('redirection', u"Permanent"))
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, db_index=True, limit_choices_to={'model__in': ['user', 'profile', 'content']}, verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(null=True, db_index=True, verbose_name=_(u"Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    content_object.short_description = _(u"Content object")
    objects = RedirectionManager()

    # Getter
    def get_new_url(self, request=None):
        """ Renvoyer l'URL de destination de la redirection """
        if hasattr(self.content_object, 'get_absolute_url'):
            query_string = "?{}".format(request.GET.urlencode()) if request else ""
            return u"{}{}".format(self.content_object.get_absolute_url(), query_string)
        return "/"

    def get_redirection_class(self):
        """ Renvoyer le type de redirection (301 ou 302) """
        return HttpResponseRedirect if not self.permanent else HttpResponsePermanentRedirect

    def get_http_code(self):
        """ Renvoyer le code HTTP de la redirection """
        return 301 if self.permanent else 302

    def get_redirect(self, request=None):
        """ Renvoyer l'objet de réponse avec la redirection """
        return self.get_redirection_class()(self.get_new_url(request))

    # Overrides
    def __init__(self, *args, **kwargs):
        """ Initialiser l'objet """
        super(Redirection, self).__init__(*args, **kwargs)

    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _(u"HTTP {http} Redirection from {base} to {new}").format(http=self.get_http_code(), base=self.base, new=self.get_new_url())

    # Métadonnées
    class Meta:
        verbose_name = _(u"redirection")
        verbose_name_plural = _(u"redirections")
        app_label = 'core'
