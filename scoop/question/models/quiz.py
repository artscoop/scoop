# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel


class Quiz(DatetimeModel, DataModel):
    """ Questionnaire """
    # Champs
    title = models.CharField(max_length=96, verbose_name=_("Title"))
    description = models.TextField(blank=False, verbose_name=_("Description"))
    questions = models.ManyToManyField('question.Question', verbose_name=_("Questions"))

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "%(title)s" % {'title': self.title}

    # Métadonnées
    class Meta:
        verbose_name = _("quiz")
        verbose_name_plural = _("quizzes")
        app_label = 'question'
