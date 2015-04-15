# coding: utf-8
from __future__ import absolute_import

from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.conf import settings
from django.db.models import Q

from scoop.core.abstract.core.datetime import DatetimeModel


@periodic_task(run_every=crontab(hour=3, minute=30, day_of_week=5))
def prune_threads(months=36):
    """
    Supprimer les sujets dont la date de modification est vieille de n mois
    Utilise settings.MESSAGIN_PRUNE_MONTHS, ou utilise 6 mois par défaut (180j)
    Par défaut tous les jeudis à minuit
    Supprime aussi les messages orphelins si nécessaire
    """
    from scoop.messaging.models.thread import Thread
    from scoop.messaging.models.message import Message
    # Date en-dessous de laquelle supprimer les sujets
    if hasattr(settings, 'MESSAGING_PRUNE_MONTHS'):
        months = settings.MESSAGING_PRUNE_MONTHS
    when = DatetimeModel.get_last_days(months * 30, timestamp=False)
    # Trouver les sujets dont la date de modification n'excède pas when
    threads = Thread.objects.filter(updated__lt=when)
    threads.update(deleted=True)
    # Trouver les messages orphelins
    messages = Message.objects.filter(Q(thread__deleted=True) | Q(thread__isnull=True))
    messages.update(deleted=True)


@periodic_task(run_every=timedelta(days=1))
def prune_alerts():
    """ Effacer les alertes lues il y a plus de n jours """
    from scoop.messaging.models.alert import Alert
    # Supptimer les alertes
    alerts = Alert.objects.read_since(2880)
    alerts.delete()


@periodic_task(run_every=timedelta(minutes=2.5))
def send_mail_queue():
    """ Expédier les mails de la file d'attente """
    from scoop.messaging.models.mailevent import MailEvent
    # Traiter séparément les catégories
    unforced = MailEvent.objects.process(forced=False)
    forced = MailEvent.objects.process(forced=True)
    return {'forced': forced, 'unforced': unforced}
