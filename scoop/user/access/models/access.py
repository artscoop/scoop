# coding: utf-8
from __future__ import absolute_import

import os
from os.path import join

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.user.ippoint import IPPointableModel
from scoop.core.util.data.dateutil import datetime_round_month, from_now
from scoop.core.util.model.csvexport import csv_dump
from scoop.core.util.stream.directory import Paths


class AccessManager(models.Manager):
    """ MAnager des accès au site """

    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(AccessManager, self).get_queryset()

    # Getter
    def path_visits(self, path, limit=20, siblings=False):
        """ Renvoyer les accès à une page ou aux pages enfants  """
        from scoop.user.access.models.page import Page
        # Siblings : Intégrer les pages ayant la même sous-URL
        if not siblings:
            visits = self.only('user').filter(page=Page.objects.get(path), user__isnull=False).order_by('-id').distinct()[:limit]
        else:
            path_start = os.path.abspath(os.path.dirname(path))
            visits = self.only('user').filter(page__path__istartswith=path_start, user__isnull=False).order_by('-id').distinct()[:limit]
        visits.query.group_by = ['user_id']
        return visits

    def by_user(self, user, limit=100):
        """ Renvoyer les accès d'un utilisateur """
        visits = self.filter(user=user).order_by('-id')
        return visits[:limit] if limit is not None else visits

    def user_ips(self, user, limit=20):
        """ Renvoyer les IPs d'un utilisateur """
        from scoop.user.access.models import IP
        # IPs
        ips = IP.objects.for_user(user)[:limit]
        return ips

    def from_datetime(self, when, minutes=10):
        """ Récupérer les accès ayant eu lieu à partir d'une date et pendant n minutes """
        start = DatetimeModel.get_timestamp(when)
        end = start + minutes * 60
        return self.filter(time__range=(start, end)).order_by('-id')

    # Actions
    def dump(self, queryset):
        """ Consiger des accès dans un fichier CSV """
        if queryset.model == Access:
            fmt = timezone.now().strftime
            filename_info = {'year': fmt("%Y"), 'month': fmt("%m"), 'week': fmt("%W"), 'day': fmt("%d"), 'hour': fmt("%H"), 'minute': fmt("%M"), 'second': fmt("%S"), 'rows': queryset.count()}
            path = join(Paths.get_root_dir('isolated', 'var', 'log'), "access-log-{year}-{month}-{day}-{hour}-{minute}-{rows}.csv".format(**filename_info))
            return csv_dump(queryset, path, compress=True)
        return False

    def purge(self, days=3, persist=False, path="site"):
        """ Supprimer les accès plus vieux que n jours"""
        rows = self.filter(time__lte=from_now(days=-days, timestamp=True))
        if persist is True:
            self.dump(rows)
        return rows.delete()

    def purge_before_month(self, persist=False, path="site"):
        """ Supprimer les accès plus anciens que 1er du mois """
        limit = Access.get_timestamp(datetime_round_month())
        rows = self.filter(time__lt=limit)
        if persist is True:
            self.dump(rows)
        return rows.delete()

    # Setter
    def add(self, request):
        """ Consigner un accès au site """
        from scoop.user.access.models import IP, Page, UserIP
        # Enregistrer l'accès uniquement si l'URL est relative
        if '://' not in request.path:
            iprecord = IP.objects.get_by_ip(request.get_ip())
            UserIP.objects.set(user=request.user, ip=iprecord)
            if settings.USER_ACCESS_RECORD is True:
                user = request.user
                page = Page.objects.get_page(request.path)
                row = Access(user=user if user.is_active else None, ip=iprecord, page=page, referrer=request.get_referrer())
                row.save()
                return True
        return False


class Access(DatetimeModel, IPPointableModel):
    """ Entrée du journal d'accès """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="access_log", verbose_name=_("User"))
    page = models.ForeignKey('access.Page', null=False, related_name='access_log', verbose_name=_("Page"))
    referrer = models.CharField(max_length=192, verbose_name=_("Referrer"))
    objects = AccessManager()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{who} has visited {what}").format(who=self.ip, what=self.page)

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.referrer = self.referrer[0:Access._meta.get_field('referrer').max_length]
        super(Access, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("access")
        verbose_name_plural = _("accesses")
        app_label = 'access'
