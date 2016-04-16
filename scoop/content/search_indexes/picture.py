# coding: utf-8
from haystack import indexes

from scoop.content.models.picture import Picture


class PictureIndex(indexes.SearchIndex, indexes.Indexable):
    """ Index de recherche des images """
    text = indexes.CharField(document=True, use_template=True)

    # Getter
    def get_model(self):
        """ Renvoyer le modèle de l'index """
        return Picture

    def index_queryset(self, using=None):
        """ Renvoyer le queryset de l'index """
        return self.get_model().objects.all()
