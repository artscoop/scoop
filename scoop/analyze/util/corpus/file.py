# coding: utf-8
import time
from os.path import join
from zipfile import ZIP_DEFLATED, ZipFile

import unicodecsv as csv
from django.utils.six import StringIO
from scoop.analyze.util.corpus.base import BaseCorpus
from scoop.analyze.util.extractors import extractor_base
from scoop.analyze.util.formatters import format_base
from scoop.analyze.util.signals import analyzer_default_format
from scoop.analyze.util.types import Dictionary, List
from scoop.core.util.stream.directory import Paths
from textblob.classifiers import MaxEntClassifier

CORPUS_PATH = ['isolated', 'database', 'classifier', 'corpus']


class FileCorpus(BaseCorpus):
    """
    Corpus stocké dans un fichier texte CSV compressé

    J'estime qu'un corpus de 2↑15 (32768) documents devrait être utilisable
    avec cette classe de corpus. Dans le cas contraire, il faudra penser
    à développer son propre module CFFI.
    """

    # Attributs
    corpus = None  # de type Dictionary (dictionnaire auquel on peut assigner des attributs)
    corpus_shadow = None  # copie de type List (les classifieurs NLTK utilisant des listes)
    classifier = None  # classifieur NLTK, initialisé dans get_corpus

    # Getter
    def get_corpus(self):
        """ Lire et peupler le corpus """
        if self.corpus is None:
            self.corpus = Dictionary()
            self.corpus.updated = time.time()
            try:
                directory = Paths.get_root_dir(*CORPUS_PATH)
                infile = '{name}.csv'.format(name=self.pathname)
                path = join(directory, '{name}.csv.zip'.format(name=self.pathname))
                # Lire le CSV dans le fichier zip
                with ZipFile(open(path, 'rb')) as zipfile:
                    buffer = StringIO(zipfile.read(infile))
                    reader = csv.reader(buffer)
                    for row in reader:
                        # 0: category, 1: doc, 2: hash
                        self.corpus[row[2]] = (row[0], row[1])
            except IOError:
                pass
        if self.corpus_shadow is None or self.corpus_shadow.updated < self.corpus.updated:
            self.corpus_shadow = List(self.corpus.values())
            self.corpus_shadow.updated = time.time()
            self.classifier = MaxEntClassifier(self.corpus_shadow, feature_extractor=extractor_base)  # ou NaiveBayesClassifier
        return self.corpus_shadow

    def classify(self, document):
        """
        Renvoyer la catégorie la plus probable pour un document

        :rtype: str
        """
        self.get_corpus()
        return self.classifier.classify(document)

    def classify_prob(self, document):
        """
        Renvoyer les probabilités de catégorie

        :rtype: nltk.probability.DictionaryProbDist
        """
        self.get_corpus()
        return self.classifier.prob_classify(document)

    # Actions
    def save(self):
        """
        Enregistrer le corpus sur disque

        :rtype: bool
        :returns: True si la sauvegarde a eu lieu, False sinon
        """
        directory = Paths.get_root_dir(*CORPUS_PATH)
        infile = '{name}.csv'.format(name=self.pathname)
        path = join(directory, '{name}.csv.zip'.format(name=self.pathname))
        # Écrire le CSV dans le fichier zip
        try:
            with ZipFile(path, 'w', ZIP_DEFLATED) as zipfile:
                buffer = StringIO()
                writer = csv.writer(buffer, delimiter=",", encoding='utf-8')
                for row in self.corpus_shadow:
                    writer.writerow(row)
                zipfile.writestr(infile, buffer.getvalue())
            return True
        except IOError:
            return False

    def train(self, document, category):
        """
        Classer un document dans une catégorie

        :returns: signature du document
        :rtype: long
        """
        self.get_corpus()
        document = format_base(document)
        document_shadow = [document]
        analyzer_default_format.send(FileCorpus, document_shadow, category)  # On passe une liste car est modifiable par les listeners
        document = "".join(document_shadow)
        signature = hash(document)
        self.corpus[signature] = (document, category)
        self.corpus.updated = time.time()
        return signature

    def retrain(self, signature, category):
        """
        Changer la catégorie d'un document déjà classifié

        :param signature: hash du document à reclassifier
        :param category: nouvelle catégorie du document
        """
        self.get_corpus()
        if self.corpus[signature][1] != category:
            self.corpus[signature] = (self.corpus[signature][0], category)
            self.corpus.updated = time.time()
            return True
        return False

    def untrain(self, signature):
        """
        Retirer du corpus

        :param signature: Hash du document
        """
        self.get_corpus()
        extracted = self.corpus.pop(signature, None)
        self.corpus.updated = time.time()
        return extracted is not None

    # Overrides
    def __init__(self, pathname, *args, **kwargs):
        """
        Initialiser le corpus avec son nom de fichier

        :param pathname: nom de fichier du  corpus sans répertoire et extension
        """
        self.pathname = pathname
