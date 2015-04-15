# coding: utf-8
"""
Données de configuration utilisateur via formulaires
Les formulaires qui permettent d'enregistrer des informations
de configuration géritent de user.util.forms.DataForm
"""
from __future__ import absolute_import

import picklefield
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel


class FormConfigurationManager(models.Manager):
    """ Manager des configurations utilisateur """

    # Getter
    def get_user_config(self, user, name, version=None):
        """ Renvoyer les données de configuration utilisateur nom/version """
        if user is not None:
            results = self.filter(user=user, name=name, version=version or u"")
            if results.exists():
                return results.first().data
        return None

    def get_template_config(self, name, version=None):
        """ Renvoyer les données de configuration templates nom/version """
        results = self.filter(user=None, name=name, version=version or u"")
        if results.exists():
            return results.first().data
        return None

    def get_template_names(self, name):
        """ Renvoyer les noms de template existants pour un nom """
        return self.filter(name=name, user=None).values_list('version', flat=True)

    # Setter
    def set_user_config(self, user, name, data, version=None):
        """ Définir une configuration utilisateur pour un nom et une version """
        if user is not None:
            if self.filter(user=user, name=name, version=version or u"").update(data=data) == 0:
                self.create(user=user, name=name, data=data, version=version or u"")
            return True
        return False

    def set_template_config(self, name, data, version=None, description=None):
        """ Définir une configuration template pour un nom et une version """
        if self.filter(user=None, name=name, version=version or u"").update(data=data, description=description or u"") == 0:
            self.create(user=None, name=name, data=data, version=version or u"", description=description or u"")
            return True


class FormConfiguration(DatetimeModel):
    """ Configuration utilisateur via formulaire """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='configurations', on_delete=models.CASCADE, verbose_name=_(u"User"))
    name = models.CharField(max_length=32, verbose_name=_(u"Form name"))
    version = models.CharField(max_length=24, blank=True, help_text=_(u"Variation name"), verbose_name=_(u"Version"))
    data = picklefield.PickledObjectField(default=dict(), compress=True, verbose_name=_("Data"))
    description = models.TextField(blank=True, verbose_name=_(u"Description"))  # only for templates, ie user=None
    objects = FormConfigurationManager()

    # Getter
    def get_data(self, name, default=None):
        """ Renvoyer les données d'un champ de la configuration """
        raw_information = self.data.get('name', default)
        return raw_information

    # Métadonnées
    class Meta:
        verbose_name = _(u"user configuration")
        verbose_name_plural = _(u"user configurations")
        unique_together = (('user', 'name', 'version'),)
        app_label = 'user'
