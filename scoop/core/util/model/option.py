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


def OptionField(name, verbose_name, null=None, blank=None, default=None, on_delete=None, related_name=None, db_index=None, multiple=False):
    """
    Renvoyer une partie de la définition d'une ForeignKey vers core.option
    default : null, blank, default none, protect on delete, db_index false, dummy related_name
    """
    attributes = {'null': null or True, 'blank': blank or True, 'default': default or None, 'db_index': db_index or False}
    attributes['limit_choices_to'] = option_group(name)
    attributes['verbose_name'] = verbose_name
    attributes['related_name'] = "{}+".format(random.randrange(0xffffffff))
    if multiple is False:
        attributes['on_delete'] = on_delete or models.PROTECT
        return models.ForeignKey('core.Option', **attributes)
    else:
        attributes.pop('null')
        attributes['blank'] = True
        attributes['default'] = []
        return models.ManyToManyField('core.Option', **attributes)
