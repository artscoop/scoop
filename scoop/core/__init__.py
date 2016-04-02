# coding: utf-8
"""
Cœur des applications scoop.

Classes abstraites pour les autres applications scoop
Modèles centraux :
- Options (choices, mais en base de données avec plus d'options)
- Recorder de tous éléments possédant un UUID
- Recorder des actions effectuées sur le système
- Redirections
Legacy pour import/export de données legacy de DB
Profiling et mesures de performances de requêtes (middleware)
"""
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop as _

__version__ = (1, 2016, 3)
_("language"), _("gender"), _("Profiles"), _("Profile")


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
        from scoop.core.abstract.rogue.flag import FlaggableModelUtil
        from scoop.core.util.model.model import patch_methods

        from django.contrib.admin.templatetags import admin_list
        from django.core.handlers.wsgi import WSGIRequest
        from django.db.models import Model

        # Patcher les classes HTTPRequest
        WSGIRequest.__bases__ += (RequestMixin,)
        WSGIRequest.__reduce__ = RequestMixin.__reduce__

        # Patcher la classe Model
        patch_methods(Model, DictUpdateModel, AdminURLUtil, ModelFormUtil, FlaggableModelUtil, get_all_related_objects)

        # Patcher l'admin
        admin_list._boolean_icon = _boolean_icon


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.core.CoreConfig'
