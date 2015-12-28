# coding: utf-8
import logging

from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.conf import settings
from django.db import transaction
from scoop.user.access.models import IP, Access

logger = logging.getLogger(__name__)


@periodic_task(run_every=crontab(minute='0', hour='4', day_of_month='*/2'))
def prune_access_log():
    """ Faire expirer les blocages d'IP """
    days = getattr(settings, 'USER_ACCESS_PRUNE_DAYS', False)
    if days and days > 0:
        Access.objects.purge(days, persist=True)


@periodic_task(run_every=timedelta(minutes=10))
def update_ip_data():
    """ Mettre à jour périodiquement les IPs existantes """
    oldest_ips = IP.objects.all().order_by('updated')[0:100]
    with transaction.atomic():
        for ip in oldest_ips:
            ip.save(force_lookup=True)
    return True
