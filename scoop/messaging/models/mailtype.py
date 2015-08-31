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
    INTERVALS = [[0, _("As soon as possible")], [5, _("Every 5 minutes")], [10, _("Every 10 minutes")], [30, _("Every 30 minutes")], [60, _("Every hour")], [720, _("Every 12 hours")],
                 [1440, _("Every day")], [4320, _("Every 3 days")], [10080, _("Every week")], [43200, _("Every 30 days")]]
    # Champs
    short_name = models.CharField(max_length=32, verbose_name=_("Codename"))
    template = models.CharField(max_length=32, help_text=_("Template filename without path and extension"), verbose_name=_("Template"))
    interval = models.IntegerField(default=0, choices=INTERVALS, help_text=_("Delay in minutes"), verbose_name=_("Minimum delay"))

    # Getter
    @addattr(short_description=_("Description"))
    def get_description(self):
        """ Renvoyer la description du type de mail """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _("(No description)")

    @addattr(admin_order_field='interval', short_description=_("Interval"))
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
        verbose_name = _("mail type")
        verbose_name_plural = _("mail types")
        app_label = "messaging"


class MailTypeTranslation(get_translation_model(MailType, "mailtype"), TranslationModel):
    """ Traduction du type de mail """
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(MailTypeTranslation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        app_label = 'messaging'
