# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager


class AttendanceManager(SingleDeleteManager):
    """ Manager des participations à des événements """
    # Constantes
    WAS_THERE, NOT_THERE, UNKNOWN = 1, 2, 0
    WONT, MIGHT, WILL = 0, 1, 2

    # Getter
    def get_by_organizer(self, author):
        """ Renvoyer les participations des événements créés par un utilisateur """
        return self.filter(event__author=author)

    def get_by_user(self, author):
        """ Renvoyer les participations d'un utilisateur """
        return self.filter(author=author)

    def get_with_forecast(self, event, forecast=MIGHT):
        """ Renvoyer les participations avec une certaine certitude """
        attendances = self.filter(event=event, forecast=forecast)
        return attendances

    def get_with_status(self, event, status=WAS_THERE):
        """ Renvoyer les participations avec un statut final """
        attendances = self.filter(event=event, status=status)
        return attendances


class Attendance(AuthoredModel):
    """ Participation à un événement """
    # Constantes
    STATUSES = [[1, _(u"I was there")], [2, _(u"I was not there")], [0, _(u"Unknown")]]
    FORECASTS = [[0, _(u"I will not participate")], [1, _(u"I might participate")], [2, _(u"I will participate")]]
    WAS_THERE, NOT_THERE, UNKNOWN = 1, 2, 0
    WONT, MIGHT, WILL = 0, 1, 2
    # Champs
    event = models.ForeignKey('social.Event', related_name='attendances', verbose_name=_(u"Event"))
    forecast = models.SmallIntegerField(choices=FORECASTS, default=MIGHT, db_index=True, verbose_name=_(u"Forecast"))
    status = models.SmallIntegerField(choices=STATUSES, default=UNKNOWN, db_index=True, verbose_name=_(u"Status"))
    objects = AttendanceManager()

    # Setter
    def foresee(self, status=MIGHT):
        """ Prévoir une participation """
        if timezone.now() < self.event.start:
            self.forecast = status
            self.save(update_fields=['forecast'])

    def review(self, status=WAS_THERE):
        """ Indiquer si l'utilisateur a participé à l'événement """
        if timezone.now() >= self.event.start:
            self.status = status
            self.save(update_fields=['status'])

    # Métadonnées
    class Meta:
        verbose_name = _(u"attendance")
        verbose_name_plural = _(u"attendances")
        unique_together = [['author', 'event']]
        app_label = "social"
