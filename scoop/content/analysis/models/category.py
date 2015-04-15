# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode


class Category(models.Model):
    """ Catégorie de document """
    # Champs
    group = models.CharField(max_length=16, db_index=True, blank=True, verbose_name=_(u"Group"))
    name = models.CharField(max_length=32, blank=False, verbose_name=_(u"Name"))
    positive = models.BooleanField(verbose_name=_(u"Positive slot or not"))

    # Getter
    @staticmethod
    def get(name, positive=True):
        """ Récupérer une catégorie dans son état Négatif ou Positif """
        category, _ = Category.objects.get_or_create(name=name, positive=positive)
        Category.objects.get_or_create(name=name, positive=not positive)
        return category

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        # Le nom de la catégorie est transformé en minuscules ASCII
        self.name = unidecode(self.name.lower())
        super(Category, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        unique_together = (('name', 'positive'),)
        verbose_name = _(u"category")
        verbose_name_plural = _(u"categories")
        app_label = 'analysis'
