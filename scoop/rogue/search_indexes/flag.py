# coding: utf-8
from haystack import indexes


class FlagIndex(indexes.SearchIndex, indexes.Indexable):
    """ Index haystack des signalements """
    text = indexes.CharField(document=True, use_template=True)

    # Getter
    def get_model(self):
        """ Renvoyer le modèle de l'index """
        from scoop.rogue.models.flag import Flag
        return Flag

    def index_queryset(self, using=None):
        """ Renvoyer les objets de l'index """
        return self.get_model().objects.all()
