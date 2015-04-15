# coding: utf-8
from __future__ import absolute_import

from celery.schedules import timedelta
from celery.task import periodic_task
from django.utils import timezone


@periodic_task(run_every=timedelta(days=1))
def prune_reads():
    """ Supprimer les marques de lecture expirées """
    from scoop.forum.models import Read
    reads = Read.objects.filter(expiry__lt=timezone.now())
    return reads.delete()
