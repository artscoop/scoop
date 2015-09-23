# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel


class QuizType(DatetimeModel, DataModel):
    """ Type de questionnaire """
    # Champs
    processor = models.CharField(max_length=128, blank=False, verbose_name=_("Results processor class name"))
    title = models.CharField(max_length=96, verbose_name=_("Title"))
    description = models.TextField(blank=False, verbose_name=_("Description"))

    # Champs supplémentaires
    backwards = models.BooleanField(default=False, verbose_name=_("Can go backwards"))
    timeout = models.SmallIntegerField(default=-1, verbose_name=_("Timeout, in seconds"))

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "%(title)s" % {'title': self.title}

    # Métadonnées
    class Meta:
        verbose_name = _("quiz type")
        verbose_name_plural = _("quiz types")
        app_label = 'question'
