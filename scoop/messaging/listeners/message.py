# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib import messages
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _

from scoop.core.templatetags.html_tags import linebreaks_convert
from scoop.core.util.signals import record
from scoop.messaging.models.message import Message
from scoop.messaging.models.recipient import Recipient
from scoop.messaging.tasks.message import check_message
from scoop.messaging.util.signals import message_pre_send, message_sent


@receiver(pre_save, sender=Message)
def defaut_pre_save(sender, instance, raw, using, **kwargs):
    """ Traiter un message avant son enregistrement """
    instance.text = linebreaks_convert(instance.text)


@receiver(message_pre_send)
def default_pre_send(sender, author, thread, **kwargs):
    """ Traiter un message avant son envoi """
    errors = set()
    # Renvoyer ok si l'auteur est du staff
    if author.is_staff or author.is_superuser or getattr(author, 'bot', False):
        return True
    # Ne rien faire si le sujet est fermé
    if thread.closed:
        errors.add(_(u"The thread is closed."))
    # Ne rien faire non plus si l'auteur ne fait pas partie du sujet
    if not thread.is_recipient(author):
        errors.add(_(u"You have no access to this thread."))
    elif getattr(settings, 'MESSAGING_BLACKLIST_ENABLE', False):
        if thread.has_blacklist(author):
            errors.add(_(u"A blacklist policy prevents you from sending your message."))
    # Renvoyer les erreurs s'il y en a
    if errors:
        return {'messages': errors}
    return True


@receiver(message_sent)
def default_post_send(sender, author, message, request, **kwargs):
    """ Traiter un message qui vient d'être envoyé """
    if request is not None:
        messages.success(request, _(u"Message sent successfully"))
    getattr(check_message, 'delay')(sender)
    # Mettre à jour le nombre de messages envoyés par user
    Recipient.objects.update_counter(author, message.thread)
    record.send(None, actor=author, action='messaging.create.message', target=message)
    return True
