# coding: utf-8
from __future__ import absolute_import

import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.weight import WeightedModel


class Question(DatetimeModel, WeightedModel):
    """ Question """
    # Constantes
    TYPES = [[0, _("Simple answers")], [1, _("Multiple answers")], [2, _("Grouped answers")]]
    # Champs
    type = models.SmallIntegerField(choices=TYPES, default=0, verbose_name=_("Quiz type"))
    title = models.CharField(max_length=96, verbose_name=_("Title"))
    description = models.TextField(blank=False, verbose_name=_("Description"))
    answers = models.TextField(blank=False, help_text=("TODO"), verbose_name=_("Answers"))

    # Getter
    def get_group_count(self):
        """ Renvoyer le nombre de groupes de réponses """
        return self.answers.count("((") or 1

    def get_group(self, index=1):
        """ Renvoyer un groupe de réponses à l'index n """
        groups = re.search(r'\(\((.*)\)\)', self.answers, re.UNICODE)
        match = groups.group(index - 1)
        labels = match.split(';;')
        return labels

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "%(title)s" % {'title': self.title}

    # Métadonnées
    class Meta:
        app_label = 'question'
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
