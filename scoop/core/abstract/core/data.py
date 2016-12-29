# coding: utf-8
import logging

import picklefield
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.model.fields import PipeListField
from scoop.core.util.shortcuts import addattr

logger = logging.getLogger(__name__)


class DataModel(models.Model):
    """ Mixin de modèle pour stocker des données """

    # Champs
    data = picklefield.PickledObjectField(default=dict, protocol=3, verbose_name=_("Data"))

    # Setter
    def set_data(self, key, value, save=False):
        """ Ajouter une clé-valeur aux données """
        if (hasattr(self, 'DATA_KEYS') and key in self.DATA_KEYS) or not hasattr(self, 'DATA_KEYS'):
            if not isinstance(self.data, dict):
                self.data = {key: value}
            else:
                self.data[key] = value
            if save is True:
                self.save(update_fields=['data'])
            return True
        else:
            return False

    def set_data_all(self, data, save=False):
        """ Redéfinir toutes les clés/valeurs en une seule fois """
        data_keys = self.get_data_keys()
        if isinstance(data, dict) and (not data_keys or all(key in data_keys for key in data.keys())):
            self.data = data
            if save is True:
                self.save(update_fields=['data'])
            return True
        logger.warning("Could not set full data field for {}. Check your DATA_KEYS attribute matches your keys.".format(str(self)))
        return False

    # Getter
    def get_data_keys(self):
        """ Renvoyer les clés de données autorisées """
        return getattr(self, 'DATA_KEYS', frozenset())

    def get_data(self, key, default=None):
        """ Renvoyer la valeur d'une clé de données """
        if self.data is None or key not in self.data:
            return default
        else:
            return self.data[key]

    @addattr(short_description=_("Data"))
    def get_data_repr(self):
        """ Renvoyer la représentation unicode des données """
        lines = []
        for key in self.data:
            value = self.get_data(key)
            if isinstance(value, list):
                info = _("{count} items").format(count=len(value))
            else:
                try:
                    info = str(value)
                except ValueError:
                    info = _("Unknown data")
            output = "{key} -> {info}".format(key=key, info=info)
            lines.append(output)
        return ", ".join(lines)

    # Métadonnées
    class Meta:
        abstract = True


class PipeListModel(models.Model):
    """ Mixin de modèle dont les données sont séparées par des pipes (|) """
    pipe_data = PipeListField(default="", verbose_name=_("Data"))

    # Setter
    def add_pipe_value(self, value):
        """ Ajouter une donnée"""
        if value not in self.get_pipe_list():
            self.pipe_data += ("|{}".format(value) if self.pipe_data else value)
            self.save()

    def remove_pipe_value(self, value):
        """ Retirer une donnée si elle existe """
        if value in self.get_pipe_list():
            clean_data = [item for item in self.get_pipe_list() if item != value]
            self.pipe_data = "|".join(clean_data)
            self.save()

    # Getter
    def get_pipe_list(self):
        """ Renvoyer les données """
        return self.pipe_data.split("|")

    # Métadonnées
    class Meta:
        abstract = True
