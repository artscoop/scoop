# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.aggregates import Avg, Sum
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.model.model import SingleDeleteManager


class ScoreManager(SingleDeleteManager):
    """ Manager de points """

    # Setter
    def add(self, author, user, count=1, axis=0):
        """ Ajouter des points à un utilisateur sur un axe """
        if author.has_perm('social.add_score'):
            score = self.get_or_create(author=author, user=user, axis=axis)
            # Ajouter les points
            score.score = count
            score.save()

    # Getter
    def get_average(self, user, axis=0):
        """ Renvoyer le score moyen d'un utilisateur sur un axe """
        points = self.filter(axis=axis)
        result = points.aggregate(average=Avg('score'))
        return result['average']

    def get_total(self, user, axis=0):
        """ Renvoyer le score total d'un utilisateur sur un axe """
        points = self.filter(axis=axis)
        result = points.aggregate(total=Sum('score'))
        return result['total']


class Score(DatetimeModel):
    """ Score utilisateur """
    # Constantes
    SCORE_AXIS = [(0, _(u"General"))]
    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='score_given', verbose_name=_(u"Author"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='score_received', verbose_name=_(u"User"))
    axis = models.SmallIntegerField(choices=SCORE_AXIS, default=0, unique=True, verbose_name=_(u"Axis"))
    score = models.IntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name=_(u"Score"))
    objects = ScoreManager()

    class Meta(object):
        """ M2tadonnées """
        verbose_name = _(u"user score")
        verbose_name_plural = _(u"user points")
        unique_together = ('author', 'user', 'axis')
        app_label = "social"
