# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel


class Quiz(DatetimeModel, DataModel):
    """ Questionnaire """
    # Champs
    title = models.CharField(max_length=96, verbose_name=_(u"Title"))
    description = models.TextField(blank=False, verbose_name=_(u"Description"))
    questions = models.ManyToManyField('question.Question', verbose_name=_(u"Questions"))

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return u"%(title)s" % {'title': self.title}

    # Métadonnées
    class Meta:
        verbose_name = _(u"quiz")
        verbose_name_plural = _(u"quizzes")
        app_label = 'question'
