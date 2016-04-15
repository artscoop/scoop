# coding: utf-8
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Envoyer les mails en file (en l'absence de Celery) """
    help = 'Send queued mails'

    def handle(self, *args, **options):
        """ Expédier les mails de la file d'attente """
        from scoop.messaging.models.mailevent import MailEvent
        # Traiter séparément les catégories
        unforced = MailEvent.objects.process(forced=False)
        forced = MailEvent.objects.process(forced=True)
        return {'forced': forced, 'unforced': unforced}

