# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SitedModel(models.Model):
    """ Objet étant attaché à une instance de site """
    sites = models.ManyToManyField('sites.Site', blank=True, null=True, verbose_name=_("Sites"))

    # Métadonnées
    class Meta:
        abstract = True
