# coding: utf-8
from abc import ABCMeta, abstractmethod

from django.db import models

from scoop.analyze.util.corpus.file import FileCorpus


class ClassifiableModel(models.Model):
    """ Mixin de modèle dont le contenu peut être classifié """

    __metaclass__ = ABCMeta

    # Attributs de classifiable
    classifications = {'language': ('fr', 'en', 'NA')}  # Obligatoire. {Fichier: Catégories}
    corpora = dict()

    # Getter
    @classmethod
    def get_corpus(cls, classification):
        if classification in cls.classifications:
            if classification not in cls.corpora:
                cls.corpora[classification] = FileCorpus(classification)
            return cls.corpora[classification]
        raise ValueError("Classification {name} is not authorized in {cls}.classifications".format(name=classification, cls=cls.__name__))

    @abstractmethod
    def get_document(self):
        raise NotImplemented("Your classifiable model must implement get_document")

    # Métadonnées
    class Meta:
        abstract = True
