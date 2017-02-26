# coding: utf-8
from celery import task
from django.utils.translation import ugettext_lazy as _


@task(expires=30)
def check_message(message):
    """
    Vérifier un message et signaler l'utilisateur

    À l'heure actuelle, signale l'utilisateur si le contenu
    contient une adresse email, ou quelque chose qui s'y apparente,
    et qui semble similaire à au moins 3 autres messages récents
    """
    from scoop.rogue.models import Flag
    # Constantes
    mail_strings = ['.com', '.fr', '.net', '.org', '@', 'adres', 'contact', 'sky']
    lower_text = message.text.lower()
    # Ne vérifier que les messages qui ont quelques spécificités
    has_mail = ([i for i in mail_strings if i in lower_text] != [])
    long_enough = len(lower_text) > 24
    # Traiter le message en signalant le posteur si pas déjà signalé
    if has_mail or long_enough:
        similar = message.get_similar_user_message_count()
        if similar >= 3:
            Flag.objects.flag(message.author, status=Flag.PENDING, automatic=True, typename='message-mail', details=_("Duplicate or similar messages"))
