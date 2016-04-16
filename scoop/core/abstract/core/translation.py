# coding: utf-8
from django.utils.translation import ugettext_lazy as _


class TranslationModel(object):
    """ Mixin de modèle de traduction """

    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("[{language}] {name}").format(language=self.language, name=_(self.model.__class__._meta.verbose_name))
