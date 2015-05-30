# coding: utf-8
from __future__ import absolute_import

from django.apps.config import AppConfig
from django.utils.translation import gettext_noop as _


__version__ = (1, 2015, 3)
_("language"), _(u"gender"), _(u"Profiles"), _(u"Profile")


class CoreConfig(AppConfig):
    """ Configuration de l'application Core """
    name = 'scoop.core'
    label = 'core'

    def ready(self):
        """ Le registre d'applications est prêt """
        from scoop.core.util.django.admin import AdminURLUtil, _boolean_icon
        from scoop.core.util.django.formutil import ModelFormUtil
        from scoop.core.util.model.model import DictUpdateModel, get_all_related_objects
        from scoop.core.util.stream.request import RequestMixin

        from django.contrib.admin.templatetags import admin_list
        from django.core.handlers.wsgi import WSGIRequest
        from django.db import models
        from django.http.request import HttpRequest

        # Patcher les classes HTTPRequest
        HttpRequest.__bases__ += (RequestMixin,)
        WSGIRequest.__bases__ += (RequestMixin,)
        WSGIRequest.__reduce__ = RequestMixin.__reduce__
        HttpRequest.__reduce__ = RequestMixin.__reduce__
        # Patcher la classe Model
        models.Model.__bases__ += (AdminURLUtil, ModelFormUtil, DictUpdateModel)
        models.Model.get_all_related_objects = get_all_related_objects
        # Patcher l'admin
        admin_list._boolean_icon = _boolean_icon

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.core.CoreConfig'
