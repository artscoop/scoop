# coding: utf-8
from __future__ import absolute_import

from haystack import indexes


class ContentIndex(indexes.SearchIndex, indexes.Indexable):
    """ Index de recherche du contenu """
    text = indexes.CharField(document=True, use_template=True)

    # Getter
    def get_model(self):
        """ Renvoyer le modèle de l'index """
        from scoop.content.models.content import Content
        return Content

    def index_queryset(self, using=None):
        """ Renvoyer le queryset de l'index """
        return self.get_model().objects.all()
