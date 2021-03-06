# coding: utf-8
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.signals import record
from scoop.messaging.util.signals import negotiation_accepted, negotiation_denied, negotiation_sent


@receiver(negotiation_sent)
def send_negotiation(sender, source, target, negotiation, **kwargs):
    """ Traiter une nouvelle négociation de discussion """
    record.send(None, actor=source, action='messaging.send.negotiation', target=target)
    # Automatiquement autoriser la négociation si l'utilisateur a la permission
    if source.has_perm('messaging.can_bypass_negotiation'):
        negotiation.accept()


@receiver(negotiation_accepted)
def accept_negotiation(sender, source, target, negotiation, **kwargs):
    """ Traiter une négociation acceptée """
    from scoop.messaging.models import Thread
    # Créer un enregistrement
    record.send(None, actor=target, action='messaging.accept.negotiation', target=source)
    subject = _("Discussion between {0} and {1}").format(target, source)
    # Créer le nouveau sujet entre les deux participants
    thread_info = Thread.objects.new(target, [source], subject, None, None, closed=False, unique=False, as_mail=False, force=False)
    thread_info['thread'].add_bot_message('negotiation-accepted', as_mail=False, data={'target': target})
    return thread_info['thread']


@receiver(negotiation_denied)
def deny_negotiation(sender, source, target, negotiation, **kwargs):
    """ Traiter une négociation refusée """
    record.send(None, actor=target, action='messaging.deny.negotiation', target=source)
