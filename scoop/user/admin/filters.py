# coding: utf-8
from __future__ import absolute_import

from datetime import timedelta

from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scoop.core.admin.filters import FirstLetterFilter


class LastOnlineFilter(SimpleListFilter):
    """ Filtre admin sur la date où les utilisateurs ont été vus en ligne """
    title = _(u"last online")
    parameter_name = 'last online'

    def lookups(self, request, model_admin):
        """ Renvoyer la liste des valeurs de filtre """
        return (
            ('today', _('today')),
            ('one', _('since yesterday')),
            ('three', _('since three days')),
            ('five', _('since five days')),
            ('twow', _('since two weeks')),
            ('onem', _('since one month')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer les utilisateurs correspondant aux valeurs du filtre """
        now = timezone.now()
        today = now.date()
        if self.value() == 'today':
            return queryset.filter(last_online__gte=today)
        if self.value() == 'one':
            return queryset.filter(last_online__gte=today - timedelta(days=1))
        if self.value() == 'three':
            return queryset.filter(last_online__gte=today - timedelta(days=3))
        if self.value() == 'five':
            return queryset.filter(last_online__gte=today - timedelta(days=5))
        if self.value() == 'twow':
            return queryset.filter(last_online__gte=today - timedelta(days=14))
        if self.value() == 'onem':
            return queryset.filter(last_online__gte=today - timedelta(days=30))


class OnlineFilter(SimpleListFilter):
    """ Filtre admin sur les profils actuellement en ligne """
    title = _(u"online")
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        """ Renvoyer la liste des valeurs de filtre """
        return (
            ('yes', _('online')),
            ('no', _('offline')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer les utilisateurs correspondant aux valeurs du filtre """
        from scoop.user.models import User, BaseProfile
        # Renvoyer les en-ligne ou hors-ligne
        if issubclass(queryset.model, User):
            if self.value() == 'yes':
                online_ids = User.get_online_set()
                return queryset.filter(pk__in=online_ids)
            if self.value() == 'no':
                online_ids = User.get_online_set()
                return queryset.exclude(pk__in=online_ids)
        elif issubclass(queryset.model, BaseProfile):
            if self.value() == 'yes':
                online_ids = User.get_online_set()
                return queryset.filter(user__pk__in=online_ids)
            if self.value() == 'no':
                online_ids = User.get_online_set()
                return queryset.exclude(user__pk__in=online_ids)


class AgeFilter(SimpleListFilter):
    """ Filtre admin sur l'âge des profils """
    title = _(u"age")
    parameter_name = 'age'

    def lookups(self, request, model_admin):
        """ Renvoyer la liste des valeurs de filtre """
        return (
            ('0', _('0 to 11')),
            ('12', _('12 to 17')),
            ('18', _('18 to 24')),
            ('25', _('25 to 34')),
            ('35', _('35 to 44')),
            ('45', _('45 to 54')),
            ('55', _('55 and greater')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer les profils correspondant aux valeurs du filtre """
        try:
            values = {'0': (0, 11), '12': (12, 17), '18': (18, 24), '25': (25, 34), '35': (35, 44), '45': (45, 54), '55': (55, 255)}
            return queryset.filter(age__range=values[self.value()])
        except:
            pass


class MailFilter(SimpleListFilter):
    """ Filtre admin sur le domaine de l'adresse email d'un profil """
    title = _(u"mail service")
    parameter_name = 'mailservice'

    def lookups(self, request, model_admin):
        """ Renvoyer la liste des valeurs de filtre """
        return (
            ('live', _('Microsoft Live Mail')),
            ('yahoo', _('Yahoo! Mail')),
            ('gmail', _('Google GMail')),
            ('sfr', _('SFR')),
            ('free', _('Free')),
            ('yandex', _('Yandex')),
            ('orange', _('Orange')),
            ('bouygues', _('Bouygues')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer les profils correspondant aux valeurs du filtre """
        if self.value() == 'live':
            return queryset.filter(Q(user__email__icontains='@live') | Q(user__email__icontains='@hotmail') | Q(user__email__icontains='@outlook') | Q(user__email__icontains='@msn.'))
        if self.value() == 'yahoo':
            return queryset.filter(user__email__icontains='@yahoo')
        if self.value() == 'gmail':
            return queryset.filter(user__email__icontains='@gmail')
        if self.value() == 'sfr':
            return queryset.filter(user__email__icontains='@sfr')
        if self.value() == 'bouygues':
            return queryset.filter(user__email__icontains='@bbox')
        if self.value() == 'free':
            return queryset.filter(user__email__icontains='@free.fr')
        if self.value() == 'yandex':
            return queryset.filter(user__email__icontains='.ru')
        if self.value() == 'orange':
            return queryset.filter(user__email__icontains='@orange')


class ImageFilter(SimpleListFilter):
    """ Filtre admin sur l'existence de photos de profil """
    title = _(u"picture")
    parameter_name = 'picture'

    def lookups(self, request, model_admin):
        """ Renvoyer la liste des valeurs de filtre """
        return (
            ('yes', _('Has pictures')),
            ('no', _('Has no picture')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer les profils correspondant aux valeurs du filtre """
        if self.value() == 'yes':
            return queryset.distinct().filter(pictures__isnull=False)
        if self.value() == 'no':
            return queryset.distinct().filter(pictures__isnull=True)


class InitialFilter(FirstLetterFilter):
    """ Filtre admin sur l'initiale du nom d'utilisateur """
    title = _(u"first username letter")
    parameter_name = 'username_l'

    def queryset(self, request, queryset):
        """ Renvoyer les profils correspondant aux valeurs du filtre """
        from scoop.user.models import BaseProfile
        # Renvoyer les profils ou les utilisateurs concernés
        value = self.value()
        field_name = 'user__username' if issubclass(queryset.model, BaseProfile) else 'username'
        if value and len(value) == 1:
            if value == '0':
                return queryset.filter(**{'{field}__regex'.format(field=field_name): r'^\d'})
            else:
                return queryset.filter(**{'{field}__istartswith'.format(field=field_name): value})
