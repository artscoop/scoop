# coding: utf-8
from __future__ import absolute_import

from traceback import print_exc

from django.template.loader import render_to_string

from scoop.core.util.data.textutil import text_to_dict


class NamedFilterManager(object):
    """ Mixin de manager pour filtres nommés """

    # Getter
    def named_set(self, name, **kwargs):
        """ Filtrer le queryset selon un dictionnaire présent dans un template """
        try:
            # Calculer le chemin de template à ouvrir
            meta = self.model._meta
            template_path = "{app}/namedfilter/{model}/{name}.txt".format(app=meta.app_label, model=meta.model_name, name=name)
            # Effectuer le rendu du template avec les arguments passés
            output = render_to_string(template_path, kwargs)
            # Convertir le template en dictionnaire
            arguments = text_to_dict(output, evaluate=True)
            return self.filter(**arguments)
        except Exception as e:
            print_exc(e)
            return self.all()
