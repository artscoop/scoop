# coding: utf-8
import random

from django.db import models


def option_group(name):
    """
    Renvoyer un dictionnaire destiné aux ForeignKeys des options

    Lorsqu'on limite un set d'options à un ensemble, on applique
    limit_to = {**filters}. Ici, on applique souvent le même filtre,
    à savoir group__short_name = nom, et active = True
    On réduit la part de code nécessaire en ne demandant que le
    group__short_name en paramètre
    """
    return {'group__short_name': name, 'active': True}


class OptionField:
    """
    Champ automatique de liaison vers core.Option

    Le champ est au choix un ManyToManyField ou un ForeignKey
    """

    # Overrides
    def __new__(cls, name, verbose_name, null=None, blank=None, default=None, on_delete=None, related_name=None, db_index=None, multiple=False, **kwargs):
        """
        Renvoyer le type de l'objet à créer

        :param name: nom de code du groupe d'options concerné par le champ, ex. 'hair_color'
        :param verbose_name: nom user friendly du champ
        :param null: indique si le champ peut prendre la valeur None
        :param blank: indique si le champ peut être laissé vide (utile pour ManyToMany)
        :param default: valeur par défaut du champ
        :param db_index: indique s'il faut créer un index sur la colonne
        :param multiple: indique si le champ est un ManyToManyField
        :param kwargs: paramètres supplémentaires de création du champ
        """
        klass = models.ManyToManyField if multiple else models.ForeignKey
        attributes = {'null': null or True, 'blank': blank or True, 'default': default or None, 'db_index': db_index or False,
                      'limit_choices_to': option_group(name), 'verbose_name': verbose_name, 'related_name': '+'}

        if multiple is False:
            attributes['on_delete'] = on_delete or models.PROTECT
        else:
            attributes.pop('null')
            attributes['blank'] = True
            attributes['default'] = []

        return klass('core.Option', **attributes)
