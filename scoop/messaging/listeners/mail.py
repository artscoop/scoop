# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch.dispatcher import receiver

from scoop.messaging.models.mailevent import MailEvent
from scoop.messaging.util.signals import mailable_event
from scoop.user.forms.configuration import ConfigurationForm


@receiver(mailable_event)
def default_mail_send(sender, category, mailtype, recipient, data, **kwargs):
    """ Traiter la mise en file d'un nouvel événement mail """
    # Vérifier la configuration
    category_options = {'message_user': 'receive_on_message', 'staff': 'receive_on_staff'}
    category_value = ConfigurationForm.get_option_for(recipient, category_options.get(category, False))
    # Vérifier que le type de mail peut-être mis en file
    if category_value is True or category in settings.MESSAGING_FORCED_TYPES or recipient.is_staff:
        if (recipient.is_active and not recipient.is_online(600)) or category in settings.MESSAGING_ONLINE_TYPES or settings.DEBUG:
            forced = category in settings.MESSAGING_FORCED_TYPES
            MailEvent.objects.queue(recipient, mailtype, data, forced=forced)


@receiver(user_logged_in)
def clear_offline_mailevents(sender, request, user, **kwargs):
    """ Supprimer les événements mails supprimables si l'utilisateur est en ligne """
    MailEvent.objects.clearable(user).delete()
