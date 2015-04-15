# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _


class FeatureCount(models.Model):
    """ Décompte d'une caractéristique dans une catégorie """
    # Champs
    feature = models.CharField(max_length=32, db_index=True, verbose_name=_(u"Feature"))
    category = models.ForeignKey('classify.Category', related_name='feature_counts', verbose_name=_(u"Feature"))
    total = models.IntegerField(default=0, verbose_name=_(u"Count"))

    # Getter
    @staticmethod
    def get(feature, category):
        """ Renvoyer le total d'une caractéristique dans une catégorie """
        try:
            return FeatureCount.objects.get(feature=feature, category=category).total
        except:
            return 0

    # Setter
    @staticmethod
    def set(feature, category, value):
        """ Définir le total d'une caractéristique d'une catégorie """
        count, _ = FeatureCount.objects.get_or_create(feature=feature, category=category)
        count.total = value
        count.save()

    @staticmethod
    def increment(feature, category):
        """ Incrémenter le total d'une caractéristique dans une catégorie """
        count = FeatureCount.get(feature, category)
        FeatureCount.set(feature, category, count + 1)

    # Métadonnées
    class Meta:
        unique_together = (('feature', 'category'),)
        verbose_name = _(u"feature count")
        verbose_name_plural = _(u"feature counts")
        app_label = 'analysis'


class CategoryCount(models.Model):
    """ Total de classifications dans une catégorie """
    # Champs
    category = models.ForeignKey('classify.Category', related_name='category_counts', verbose_name=_(u"Feature"))
    total = models.IntegerField(default=0, verbose_name=_(u"Count"))

    # Getter
    @staticmethod
    def get(category):
        """ Renvoyer le nombre de caractéristiques dans la catégorie """
        try:
            return CategoryCount.objects.get(category=category).total
        except:
            return 0

    # Setter
    @staticmethod
    def set(category, value):
        """ Définir le total de caractéristiques dans la catégorie """
        count, _ = CategoryCount.objects.get_or_create(category=category)
        count.total = value
        count.save()

    @staticmethod
    def increment(category):
        """ Incrémenter le total de caractéristiques dans la catégorie """
        count = CategoryCount.get(category)
        CategoryCount.set(category, count + 1)

    # Métadonnées
    class Meta:
        verbose_name = _(u"category train count")
        verbose_name_plural = _(u"category train counts")
        app_label = 'analysis'
