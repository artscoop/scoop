# coding: utf-8
import logging
from multiprocessing.dummy import Pool

from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.conf import settings
from django.db import transaction
from celery import task

from scoop.user.access.models import IP, Access


logger = logging.getLogger(__name__)


@periodic_task(run_every=crontab(minute=0, hour=2, day_of_month='*/7'), options={'expires': 3600})
def prune_access_log():
    """ Faire expirer les blocages d'IP """
    days = getattr(settings, 'USER_ACCESS_PRUNE_DAYS', False)
    if days and days > 0:
        Access.objects.purge(days, persist=True)


@periodic_task(run_every=timedelta(seconds=36), rate_limit='6/m', options={'expires': 3600})
def update_ip_data():
    """ Mettre à jour périodiquement les IPs existantes (environ 1 200 minutes pour 500 000 enregistrements) """
    pool = Pool(16)  # 16 "threads" simultanés pour le traitement
    ips = IP.objects.order_by('updated').values_list('string', flat=True)[0:256]
    # Récupérer toutes les données d'IP des workers
    data = pool.map(IP.get_ip_information, ips)
    pool.close()
    pool.join()
    # Et modifier les ips dans le thread principal
    with transaction.atomic():
        for item in data:
            ip = IP.objects.get(ip=item['ip'])
            ip.set_ip_information(item, save=True)
    return True
