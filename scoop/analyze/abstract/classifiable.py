# coding: utf-8
from abc import ABCMeta, abstractmethod

from django.db import models
from scoop.analyze.util.corpus.file import FileCorpus


class ClassifiableModel(models.Model):
    """
    Mixin de modèle dont le contenu peut être classifié

    classifications : dictionnaire dont les clés sont des noms de fichier, et les valeurs
    des tuples contenant les catégories possibles pour le type de classification.
    Les noms de fichiers dans classifications sont exprimés sous la forme <name>, et
    le fichier correspondant dans le système de fichiers se trouve dans CORPUS_PATH
    (par défaut 'isolated/database/classifier/corpus'), et porte l'extension .csv.zip

    corpora : dictionnaire des corpus, dont les clés sont les mêmes que pour classifications.
    Les valeurs sont des corpus. Un corpus existe sous la forme d'un dictionnaire, dont les
    clés sont des hash de document, et dont les valeurs sont des tuples (document, catégorie)
    """

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
