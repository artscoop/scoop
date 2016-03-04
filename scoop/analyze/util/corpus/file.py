# coding: utf-8
import csv
import time
from os.path import join
from zipfile import ZipFile, ZIP_DEFLATED

from django.utils.six import StringIO
from textblob.classifiers import MaxEntClassifier

from scoop.analyze.util.corpus.base import BaseCorpus
from scoop.analyze.util.types import AtttributeDict, AttributeList
from scoop.core.util.stream.directory import Paths


CORPUS_PATH = ['isolated', 'database', 'classifier', 'corpus']


class FileCorpus(BaseCorpus):
    """ Corpus stocké dans un fichier texte CSV compressé """

    # Attributs
    corpus = None
    corpus_shadow = None
    classifier = None

    def get_set(self):
        """ Lire et peupler le corpus """
        if self.corpus is None:
            self.corpus = AtttributeDict()
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
            self.corpus_shadow = AttributeList(self.corpus.values())
            self.corpus_shadow.updated = time.time()
            self.classifier = MaxEntClassifier(self.corpus_shadow)  # ou NaiveBayesClassifier
        return self.corpus_shadow

    def untrain(self, signature):
        """ Retirer du corpus """
        self.get_set()
        self.corpus.pop(signature, None)
        self.corpus.updated = time.time()

    def save(self):
        directory = Paths.get_root_dir(*CORPUS_PATH)
        infile = '{name}.csv'.format(name=self.pathname)
        path = join(directory, '{name}.csv.zip'.format(name=self.pathname))
        # Écrire le CSV dans le fichier zip
        with ZipFile(path, 'w', ZIP_DEFLATED) as zipfile:
            buffer = StringIO()
            writer = csv.writer(buffer, delimiter=",")
            for row in self.corpus_shadow:
                writer.writerow(row)
            zipfile.writestr(infile, buffer.getvalue())

    def train(self, document, category):
        self.get_set()
        signature = hash(document)
        self.corpus[signature] = (document, category)

    def classify(self, document):
        self.get_set()
        return self.classifier.classify(document)

    # Overrides
    def __init__(self, pathname, *args, **kwargs):
        self.pathname = pathname
