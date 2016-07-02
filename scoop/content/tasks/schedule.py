# coding: utf-8
from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from easy_thumbnails.files import generate_all_aliases
from scoop.content.models.picture import Picture
from scoop.core.util.django.sitemaps import ping_feed


@periodic_task(run_every=timedelta(hours=48), options={'expires': 3600})
def clean_transient_pictures():
    """ Supprimer les images volatiles de plus de 24 heures """
    limit = timezone.now() - timedelta(hours=2)
    pictures = Picture.objects.filter(transient=True, updated__lt=limit)
    for picture in pictures:
        picture.delete(clear=True)


@periodic_task(run_every=timedelta(hours=4), options={'expires': 3600})
def update_unsized_pictures():
    """ Mettre à jour les dimensions des images sans dimensions """
    with transaction.atomic():
        pictures = Picture.objects.filter(width__in=[0, 1], height__in=[0, 1]).order_by('?')[:256]
        for picture in pictures:
            picture.update_size()
    return True


@periodic_task(run_every=timedelta(hours=8), options={'expires': 3600})
def create_random_picture_aliases():
    """ Créer toutes les miniatures pour des images aléatoires """
    # TODO: Vérifier le queryset ici
    with transaction.atomic():
        pictures = Picture.objects.filter(width__in=[0, 1], height__in=[0, 1]).order_by('?')[:2048]
        for picture in pictures:
            generate_all_aliases(picture.image, include_global=True)
    return True


@periodic_task(run_every=timedelta(hours=12), options={'expires': 3600})
def web_ping():
    """ Pinger le sitemap aux moteurs RSS """
    if getattr(settings, 'CONTENT_WEBLOG_PING', False):
        return ping_feed("sitemap-section", [], {'section': 'content'})
