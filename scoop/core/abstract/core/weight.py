# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _


class WeightedModel(models.Model):
    """ Objet ayant un poids, les poids les plus faibles sont en surface """
    # Constantes
    WEIGHTS = ((x, x) for x in xrange(0, 100))
    # Champs
    weight = models.SmallIntegerField(db_index=True, null=False, choices=WEIGHTS, default=10, help_text=_(u"Items with lower weights come first"), verbose_name=_(u"Weight"))

    # Métadonnées
    class Meta:
        abstract = True


class PriorityModel(models.Model):
    """ Objet ayant une priorité, les priorités élevées passent en premier """
    # Constantes
    WEIGHTS = ((x, x) for x in xrange(0, 100))
    # Champs
    weight = models.SmallIntegerField(db_index=True, null=False, choices=WEIGHTS, default=10, help_text=_(u"Items with lower weights have lower priority"), verbose_name=_(u"Weight"))

    # Setter
    def increase_priority(self, save=True, amount=1):
        """ Augmenter la priorité de l'objet """
        self.weight += amount
        if save is True:
            self.save(update_fields=['weight'])

    def decrease_priority(self, save=True, amount=1):
        """ Réduire la priorité de l'objet """
        self.increase_priority(save=save, amount=-amount)

    # Métadonnées
    class Meta:
        abstract = True
