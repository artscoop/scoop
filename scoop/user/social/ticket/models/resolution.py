# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Resolution(models.Model):
    """ Type de résolution d'un ticket """
    name = models.CharField(max_length=48, verbose_name=_(u"Name"))
    short = models.CharField(max_length=8, verbose_name=_(u"Short name"))
    description = models.TextField(blank=True, verbose_name=_(u"Description"))
    closing = models.BooleanField(default=False, help_text=_(u"Does this mean ticket closure ?"), verbose_name=_(u"Closing"))

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return u"{name}".format(name=self.name)

    # Métadonnées
    class Meta:
        verbose_name = _(u"resolution status")
        verbose_name_plural = _(u"resolution statuses")
        app_label = 'ticket'
