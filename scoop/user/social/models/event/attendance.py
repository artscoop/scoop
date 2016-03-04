# coding: utf-8
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager


class AttendanceManager(SingleDeleteManager):
    """ Manager des participations à des événements """

    # Constantes
    WAS_THERE, NOT_THERE, UNKNOWN = 1, 2, 0
    UNKNOWN, WONT, MIGHT, WILL = 0, 1, 2, 3

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
    STATUSES = [[1, _("I was there")], [2, _("I was not there")], [0, _("Unknown")]]
    FORECASTS = [[0, _("N/A")], [1, _("I will not participate")], [2, _("I might participate")], [3, _("I will participate")]]
    WAS_THERE, NOT_THERE, UNKNOWN = 1, 2, 0
    UNKNOWN, WONT, MIGHT, WILL = 0, 1, 2, 3

    # Champs
    event = models.ForeignKey('social.Event', related_name='attendances', verbose_name=_("Event"))
    forecast = models.SmallIntegerField(choices=FORECASTS, default=MIGHT, db_index=True, verbose_name=_("Forecast"))
    status = models.SmallIntegerField(choices=STATUSES, default=UNKNOWN, db_index=True, verbose_name=_("Status"))
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
        verbose_name = _("attendance")
        verbose_name_plural = _("attendances")
        unique_together = [['author', 'event']]
        app_label = "social"
