# coding: utf-8
from __future__ import absolute_import

from haystack import indexes


class MessageIndex(indexes.SearchIndex, indexes.Indexable):
    """ Index Haystack des messages """
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateField(model_attr='get_datetime')
    author = indexes.CharField(model_attr='name')

    # Getter
    def get_model(self):
        """ Renvoyer le modèle de l'index """
        from scoop.messaging.models.message import Message
        return Message

    def index_queryset(self, using=None):
        """ Renvoyer les éléments de l'index """
        return self.get_model().objects.filter(deleted=False)
