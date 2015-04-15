# coding: utf-8
from __future__ import absolute_import

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model

from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.util.shortcuts import addattr


class MailType(TranslatableModel):
    """ Type de mail """
    # Constantes
    INTERVALS = [[0, _(u"As soon as possible")], [5, _(u"Every 5 minutes")], [10, _(u"Every 10 minutes")], [30, _(u"Every 30 minutes")], [60, _(u"Every hour")], [720, _(u"Every 12 hours")],
                 [1440, _(u"Every day")], [4320, _(u"Every 3 days")], [10080, _(u"Every week")], [43200, _(u"Every 30 days")]]
    # Champs
    short_name = models.CharField(max_length=32, verbose_name=_(u"Codename"))
    template = models.CharField(max_length=32, help_text=_(u"Template filename without path and extension"), verbose_name=_(u"Template"))
    interval = models.IntegerField(default=0, choices=INTERVALS, help_text=_(u"Delay in minutes"), verbose_name=_(u"Minimum delay"))

    # Getter
    @addattr(short_description=_(u"Description"))
    def get_description(self):
        """ Renvoyer la description du type de mail """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _(u"(No description)")

    @addattr(admin_order_field='interval', short_description=_(u"Interval"))
    def get_interval(self):
        """ Renvoyer l'intervalle d'envoi pour ce type de mail """
        return datetime.timedelta(minutes=self.interval)

    # Propriétés
    description = property(get_description)

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.short_name

    # Métadonnées
    class Meta:
        verbose_name = _(u"mail type")
        verbose_name_plural = _(u"mail types")
        app_label = "messaging"


class MailTypeTranslation(get_translation_model(MailType, "mailtype"), TranslationModel):
    """ Traduction du type de mail """
    description = models.TextField(blank=True, verbose_name=_(u"Description"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(MailTypeTranslation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        app_label = 'messaging'
