# coding: utf-8
from abc import ABCMeta, abstractmethod


class BaseCorpus:
    """ Loader de base de corpus d'entraînement """
    __metaclass__ = ABCMeta

    # Atttributs
    pathname = None  # Nom du corpus. Permet de retrouver le nom de fichier.

    # Overrides
    def __init__(self, pathname, *args, **kwargs):
        """ Initialiser le loader avec un fichier de corpus """
        self.pathname = pathname
        super().__init__(*args, **kwargs)

    # Getter
    @abstractmethod
    def get_set(self):
        """ Renvoie le set de corpus """
        raise NotImplemented()

    # Setter
    @abstractmethod
    def train(self, document, category):
        """
        Ajoute un document au corpus avec une catégorie

        :type document: str
        :type category: str
        :param document: Texte, phrase ou mot à classer dans une catégorie
        :param category: Nom de catégorie.
        """
        raise NotImplemented()

    @abstractmethod
    def untrain(self, signature):
        """ Retire du corpus un document avec le hash passé """
        raise NotImplemented()

    @abstractmethod
    def classify(self, document):
        """ Renvoyer la classe détectée du document """

    @abstractmethod
    def save(self):
        """ Réécrit le corpus mis à jour """
        raise NotImplemented()

