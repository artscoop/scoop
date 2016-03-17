# coding: utf-8
from celery.schedules import timedelta
from celery.task import periodic_task


@periodic_task(run_every=timedelta(days=1))
def prune_reads():
    """ TODO: Supprimer les marques de lecture expirées """
    pass
