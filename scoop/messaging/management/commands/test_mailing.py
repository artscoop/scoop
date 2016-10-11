# coding: utf-8
from traceback import print_exc

from django.core.management.base import BaseCommand
from scoop.messaging.util.signals import mailable_event


class Command(BaseCommand):
    """ Envoyer les mails en file (en l'absence de Celery) """
    help = 'Send a generic email to superusers to check everything is ok'
    args = ''

    def handle(self, *args, **options):
        """ Expédier les mails de la file d'attente """
        from scoop.messaging.models import MailEvent
        from scoop.user.models import User
        # Mettre en file un mail de test
        try:
            mailable_event.send(None, mailtype='test.mail.base', recipient=User.objects.superusers(), data={'items': [10, 15, 20]})
            mailable_event.send(None, mailtype='test.mail.base', recipient=User.objects.superusers(), data={'items': [25, 30, 35]})
            unforced = MailEvent.objects.process(forced=False)
            forced = MailEvent.objects.process(forced=True)
        except Exception as e:
            print_exc(e)

        return "{total} mails sent with {forced} forced.".format(total=unforced + forced, forced=forced)
