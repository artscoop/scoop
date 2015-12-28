# coding: utf-8
from haystack import indexes


class CityIndex(indexes.SearchIndex, indexes.Indexable):
    """ Index haystack des villes """
    information = indexes.CharField(document=True, use_template=True)
    code = indexes.CharField(model_attr='code')
    country = indexes.CharField(use_template=True)

    # Getter
    def get_model(self):
        """ Renvoyer le modèle de l'index """
        from scoop.location.models import City
        return City

    def index_queryset(self, using=None):
        """ Renvoyer les objets de l'index """
        return self.get_model().objects.all()
