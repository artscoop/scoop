# coding: utf-8
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Envoyer les mails en file (en l'absence de Celery) """
    help = 'Send queued mails'
    args = ''

    def handle(self, *args, **options):
        """ Expédier les mails de la file d'attente """
        from scoop.messaging.models.mailevent import MailEvent
        # Traiter séparément les catégories
        unforced = MailEvent.objects.process(forced=False)
        forced = MailEvent.objects.process(forced=True)
        return "{total} mails sent with {forced} forced.".format(total=unforced + forced, forced=forced)
