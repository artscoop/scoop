# coding: utf-8
from __future__ import absolute_import

from datetime import timedelta

from celery.task import periodic_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from scoop.content.models.picture import Picture
from scoop.core.util.django.sitemaps import ping_feed


@periodic_task(run_every=timedelta(hours=10))
def clean_transient_pictures():
    """ Supprimer les images volatiles de plus de 24 heures """
    limit = timezone.now() - timedelta(hours=2)
    pictures = Picture.objects.filter(transient=True, updated__lt=limit)
    for picture in pictures:
        picture.delete(clear=True)


@periodic_task(run_every=timedelta(minutes=4))
def update_unsized_pictures():
    """ Mettre à jour les dimensions des images sans dimensions """
    with transaction.atomic():
        pictures = Picture.objects.filter(width__in=[0, 1, None], height__in=[0, 1, None]).order_by('?')[:256]
        for picture in pictures:
            picture.update_size()
    return True


@periodic_task(run_every=timedelta(hours=13))
def web_ping():
    """ Pinger le sitemap aux moteurs RSS """
    if getattr(settings, 'CONTENT_WEBLOG_PING', False):
        return ping_feed("sitemap-section", [], {'section': 'content'})
