# coding: utf-8
from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.apps.registry import apps
from django.conf import settings
from django.core.management import call_command
from scoop.core.models.recorder import Record
from scoop.core.models.redirection import Redirection
from scoop.core.models.uuidentry import UUIDEntry
from scoop.core.util.data.dateutil import from_now
from scoop.core.util.stream.fileutil import clean_empty_folders, clean_orphans


@periodic_task(run_every=timedelta(days=7), options={'expires': 3600})
def clean_media_folders():
    """ Nettoyer les fichiers orphelins des répertoires MEDIA """
    if apps.is_installed('scoop.content'):
        from scoop.content.models.picture import Picture
        # Nettoyer les miniatures
        Picture.objects.clean_thumbnails()
    # Supprimer les fichiers sans référence
    clean_orphans(output_log=False, delete=True)
    clean_empty_folders(settings.MEDIA_ROOT)


@periodic_task(run_every=timedelta(days=1), options={'expires': 3600})
def update_search_index():
    """ Mettre à jour l'index Haystack """
    call_command('update_index', age=2, batchsize=1000)


@periodic_task(run_every=timedelta(days=7), options={'expires': 3600})
def vacuum_postgres_database():
    """ Vacuum Full pour les bases de données Postgres """
    from django.db import connection, connections
    # VACUUM pour PostgreSQL
    if 'postgres' in connections.databases['default']['ENGINE']:
        cursor = connection.cursor()
        cursor.execute('VACUUM FULL')
        cursor.close()
        return True
    return False


@periodic_task(run_every=timedelta(days=2), options={'expires': 3600})
def update_uuid_registry():
    """ Mettre à jour le registre des UUID """
    UUIDEntry.objects.populate()


@periodic_task(run_every=timedelta(days=1), rate_limit='1/h', options={'expires': 3600})
def backup_database():
    """ Effectuer un backup de la base de données """
    if apps.is_installed('dbbackup'):
        call_command('dbbackup', clean=True, compress=True, encrypt=False, database='default')


@periodic_task(run_every=timedelta(days=1), options={'expires': 3600})
def purge_redirections():
    """ Désactiver les redirections qui ont expiré """
    Redirection.objects.get_expired().update(active=False)


@periodic_task(run_every=timedelta(days=30), options={'expires': 86400 * 15})
def purge_records():
    """ Purger les enregistrements plus vieux que 600 jours """
    records = Record.objects.filter(created__lt=from_now(days=-600))
    Record.objects.dump(records)
    records.delete()
