# coding: utf-8
import datetime

from django.contrib.admin.filters import SimpleListFilter
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.data.dateutil import now as now_


class FirstLetterFilter(SimpleListFilter):
    """ Filtre admin sur la première lettre du champ name """
    title = _("first letter")
    parameter_name = 'firstlt'

    def lookups(self, request, model_admin):
        """ Renvoyer les valeurs possibles de filtre """
        letters = [(letter, letter) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        letters.append(('0', '0-9'))
        return letters

    def queryset(self, request, queryset):
        """ Renvoyer un queryset d'objets correspondant aux valeurs de filtre """
        value = self.value()
        if value and len(value) == 1:
            if value == '0':
                return queryset.filter(name__regex=r'^\d')
            else:
                return queryset.filter(name__istartswith=self.value())


class RandomOrderFilter(SimpleListFilter):
    """ Filtre admin de tri aléatoire """
    title = _("random")
    parameter_name = 'randomize'

    def lookups(self, request, model_admin):
        """ Renvoyer les valeurs possibles du filtre """
        return (('yes', _("Yes")),)

    def queryset(self, request, queryset):
        """ Renvoyer un queryset mélangé ou ordonné """
        if self.value() == 'yes':
            return queryset.order_by('?')


class TimestampFilter(SimpleListFilter):
    """ Filtre admin pour les objets DatetimeModel """
    title = _("date and time")
    parameter_name = 'time'

    def lookups(self, request, model_admin):
        """ Renvoyer les valeurs possibles de filtre """
        today = timezone.now()
        day, month, year = today.strftime('%A,%B,%Y').decode('utf-8').split(',')
        return (('l24', _("last 24 hours")), ('l72', _("last 72 hours")), ('lweek', _("past 7 days")), ('lmonth', _("past 30 days")),
                ('today', _("today ({day})").format(day=day)), ('month', _("this month ({month})").format(month=month)), ('month-1', _("last month")),
                ('year', _("this year ({year})").format(year=year)), ('year-1', _("last year")),)

    def queryset(self, request, queryset):
        """ Renvoyer un queryset correspondant aux valeurs du filtre """
        int_now = now_()
        now = timezone.now()
        now_month = datetime.datetime(year=now.year, month=now.month, day=1)
        now_last_month = datetime.datetime(year=(now_month - datetime.timedelta(days=1)).year, month=(now_month - datetime.timedelta(days=1)).month, day=1)
        if self.value() == 'l24':
            return queryset.filter(time__gte=int_now - 86400)
        if self.value() == 'l72':
            return queryset.filter(time__gte=int_now - 86400 * 3)
        if self.value() == 'lweek':
            return queryset.filter(time__gte=int_now - 86400 * 7)
        if self.value() == 'lmonth':
            return queryset.filter(time__gte=int_now - 86400 * 30)
        if self.value() == 'today':
            return queryset.filter(time__gte=DatetimeModel.get_timestamp(now.date()))
        if self.value() == 'month':
            return queryset.filter(time__gte=DatetimeModel.get_timestamp(now_month))
        if self.value() == 'month-1':
            return queryset.filter(time__range=[DatetimeModel.get_timestamp(now_last_month), DatetimeModel.get_timestamp(now_month)])
        if self.value() == 'year':
            return queryset.filter(time__gte=DatetimeModel.get_timestamp(datetime.datetime(year=now.year)))
        if self.value() == 'year-1':
            return queryset.filter(time__range=[DatetimeModel.get_timestamp(datetime.datetime(now.year - 1, 1, 1)), DatetimeModel.get_timestamp(datetime.datetime(now.year, 1, 1))])
