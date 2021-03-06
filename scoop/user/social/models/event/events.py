# coding: utf-8
import datetime

from crontab._crontab import CronTab
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.social.access import PrivacyModel
from scoop.core.abstract.social.invite import InviteTargetModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteQuerySetMixin
from scoop.user.social.models.event.attendance import Attendance


class OccurrenceQuerySetMixin(object):
    """ Mixin Queryset et Manager des récurrences d'événements """

    # Getter
    def open(self, **kwargs):
        """ Renvoyer les événements ouverts aux inscriptions """
        return self.filter(status=0)

    def closed(self, **kwargs):
        """ Renvoyer les événements fermés """
        return self.filter(status=1)

    def from_now(self, hours=24):
        """ Renvoyer les événements des n prochaines heures """
        now = timezone.now()
        then = now + datetime.timedelta(hours=hours)
        return self.filter(models.Q(date__range=(now, then)) | models.Q(end__range=(now, then)))

    def finished(self):
        """ Renvoyer les événements terminés """
        return self.filter(end__lt=timezone.now())

    def by_city(self, city, **kwargs):
        """ Renvoyer les événements par ville """
        return self.filter(address__city=city, **kwargs)

    def by_country(self, country, **kwargs):
        """ Renvoyer les événements par pays """
        return self.filter(address__city__country=country, **kwargs)

    def at_date(self, when, event):
        """ Indiquer si un événement est en collision avec une date """
        return self.filter(date__lte=when, end_gte=when, event=event)

    def exists_at_date(self, when, event):
        """ Indiquer si un événement est en collision avec une date """
        return self.at_date(when=when, event=event).exists()


class OccurrenceQuerySet(models.QuerySet, SingleDeleteQuerySetMixin, OccurrenceQuerySetMixin):
    """ Queryset des récurrences d'événements """
    pass


class OccurrenceManager(models.Manager.from_queryset(OccurrenceQuerySet), models.Manager, OccurrenceQuerySetMixin):
    """ Manager des récurrences d'événements """
    pass


class Event(AuthoredModel, DatetimeModel, PicturableModel, PrivacyModel, DataModel, UUID64Model):
    """ Événement """

    # Constantes
    DATA_KEYS = ['privacy', 'crontab']

    # Champs
    title = models.CharField(max_length=128, blank=False, verbose_name=_("Title"))
    description = models.TextField(blank=False, verbose_name=_("Description"))
    categories = models.ManyToManyField('social.EventCategory', related_name='events', verbose_name=_("Categories"))
    address = models.ForeignKey('location.Venue', null=True, blank=True, related_name='events', verbose_name=_("Address"))
    capacity = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(999)], verbose_name=_("Max attendants"))

    # Getter
    def get_occurrences(self):
        """ Renvoyer les récurrences de l'événement """
        return self.occurrences.all()

    def get_occurrence_count(self):
        """ Renvoyer le nomnre de récurrences de l'événement """
        return self.occurrences.count()

    # Setter
    def add_occurrence(self, when, force=False):
        """
        Ajouter une occurrence à l'événement (si elle n'existe pas)

        :returns: True si l'occurrence a été ajoutée, False sinon
        :param when: Date de l'occurrence
        :param force: forcer l'insertion même si conflit avec une autre occurrence du même événement
        """
        if not Occurrence.objects.exists_at_date(when, self) or force:
            occurrence = Occurrence(event=self, date=when, description=self.description)
            occurrence.save()
            return True
        return False

    def set_crontab(self, crontab):
        """
        Définir la récurrence via une chaîne compatible crontab

        :type crontab: str
        :param crontab: chaîne compatible avec les règles cron, voir https://github.com/josiahcarlson/parse-crontab
        """
        self.set_data('crontab', crontab, save=True)

    def add_crontab_occurrences(self, count=2):
        """ Ajouter des occurrences selon le crontab """
        crontab = self.get_data('crontab', '')
        scheduler = CronTab(crontab)
        occurrence_time = timezone.now()
        occurrences_added = 0
        for index in range(count):
            delay = scheduler.next(now=occurrence_time)
            occurrence_time += delay
            success = self.add_occurrence(occurrence_time)
            occurrences_added += 1 if success else 0
        return occurrences_added

    def clear_occurrences(self):
        """ Supprimer toutes les occurrences de l'événement """
        self.get_occurrences().delete()

    # Métadonnées
    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        app_label = "social"


class Occurrence(DatetimeModel, InviteTargetModel, UUID64Model):
    """ Récurrence d'événement """

    # Constantes
    DEFAULT_CAPACITY = 20
    STATUSES = [[0, _("Open")], [1, _("Closed")], [2, _("Cancelled")]]
    OPEN, CLOSED, CANCELLED = 0, 1, 2

    # Champs
    event = models.ForeignKey('social.Event', related_name='occurrences', verbose_name=_("Event"))
    status = models.SmallIntegerField(default=0, choices=STATUSES, db_index=True, verbose_name=_("Status"))
    title = models.CharField(max_length=128, blank=True, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    date = models.DateTimeField(null=False, verbose_name=_("Date"))
    duration = models.IntegerField(default=60, validators=[MinValueValidator(15)], help_text=_("In minutes"), verbose_name=_("Duration"))
    end = models.DateTimeField(editable=False, verbose_name=_("Auto"))  # utilisé pour l'ORM
    address = models.ForeignKey('location.Venue', null=True, blank=True, related_name='event_occurrences', verbose_name=_("Address"))
    capacity = models.IntegerField(default=DEFAULT_CAPACITY, validators=[MinValueValidator(1), MaxValueValidator(999)], verbose_name=_("Max attendants"))
    group = models.CharField(max_length=11, blank=True, db_index=True, verbose_name=_("Group"))
    objects = OccurrenceManager()

    # Getter
    def can_add(self):
        """ Renvoyer si l'événement accepte de nouveaux inscrits """
        return self.get_remaining() > 0

    def get_remaining(self):
        """ Renvoyer le nombre de places restantes pour l'événement """
        return (self.capacity - self.attendances.exclude(status=0).count()) if self.status not in {self.CLOSED, self.CANCELLED} else 0

    def get_end(self):
        """ Renvoyer la date de fin de l'événement """
        return self.date + timezone.timedelta(minutes=self.duration)

    def get_start(self):
        """ Renvoyer la date de départ """
        return self.date

    def has_attendant(self, user):
        """ Renvoyer si un utilisateur participe à l'événement """
        return self.attendances.filter(user=user).exists()

    def get_attendance(self, user):
        """ Renvoyer la participation d'un utilisateur """
        if self.has_attendant(user):
            return self.attendances.get(user=user)
        return None

    def get_time_elapsed(self):
        """ Renvoyer le temps écoulé de l'événement """
        if self.has_begun() and not self.is_over():
            return timezone.now() - self.get_start()
        return None

    def get_time_remaining(self):
        """ Renvoyer le temps restant avant la fin de l'événement """
        now = timezone.now()
        return self.get_end() - now if self.get_end() > now else None

    def get_time_completion(self):
        """ Renvoyer le pourcentage de progression de l'événement en temps réel """
        duration, elapsed = self.get_duration(), self.get_elapsed()
        return 100.0 * elapsed / duration if elapsed is not None else None

    def get_duration(self):
        """ Renvoyer la durée prévue de l'événement """
        return self.duration

    def get_time_frame(self):
        """ Renvoyer la date de début et la date de fin de l'événement """
        return [self.get_start(), self.get_end()]

    def has_begun(self):
        """ Renvoyer si l'événement a commencé """
        return self.get_start() < timezone.now() <= self.get_end()

    def is_over(self):
        """ Renvoyer si l'événement est terminé """
        return self.get_end() < timezone.now()

    # Setter
    def add_attendance(self, user, forecast=Attendance.WONT):
        """ Ajouter un participant """
        if user and user.is_active:
            from scoop.user.social.models import Attendance
            # Ajouter uniquement si possible
            if self.can_add():
                Attendance.objects.create(author=user, event=self, forecast=forecast)

    def remove_attendance(self, user):
        """ Retirer un participant """
        if self.has_attendant(user):
            self.get_attendance(user).delete()

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.get_end() is None or self.duration < 15:
            self.duration = 15
        self.end = self.get_end()
        super().save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("event occurrence")
        verbose_name_plural = _("event occurrences")
        app_label = "social"
