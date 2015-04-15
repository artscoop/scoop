# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.content.analysis.classifiers.base import BaseClassifier
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel


class Document(DatetimeModel, DataModel):
    """ Corpus """
    # Champs
    text = models.TextField(unique=True, verbose_name=_(u"Text"))
    category = models.ForeignKey('classify.Category', null=True, related_name='documents', verbose_name=_(u"Category"))

    # Setter
    @staticmethod
    def set(text, category):
        """ Ajouter un document dans une catégorie """
        document, _ = Document.objects.get_or_create(text=text.lower(), category=category)
        return document

    # Actions
    def classify(self, category):
        """ Classifier le document dans une catégorie """
        BaseClassifier().learn(self, category)
        self.category = category
        self.save()

    # Métadonnées
    class Meta:
        verbose_name = _(u"document")
        verbose_name_plural = _(u"documents")
        app_label = 'analysis'
