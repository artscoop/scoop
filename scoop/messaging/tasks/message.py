# coding: utf-8
from celery import task
from django.utils.translation import ugettext_lazy as _


@task
def check_message(message):
    """ Vérifier un message """
    from scoop.rogue.models import Flag
    # Constantes
    MAIL_STRINGS = ['.com', '.fr', '.net', '.org', '@', 'adres', 'contact', 'sky']
    LOWER_TEXT = message.text.lower()
    # Ne vérifier que les messages qui ont quelques spécificités
    has_mail = ([i for i in MAIL_STRINGS if i in LOWER_TEXT] != [])
    long_enough = len(LOWER_TEXT) > 24
    # Traiter le message en signalant le posteur si pas déjà signalé
    if has_mail or long_enough:
        similar = message.get_similar_user_message_count()
        if similar >= 3:
            Flag.objects.flag(message.author, status=Flag.PENDING, automatic=True, typename='message-mail', details=_("Duplicate or similar messages"))
