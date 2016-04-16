# coding: utf-8
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.signals import record
from scoop.messaging.models.quota import Quota
from scoop.messaging.models.recipient import Recipient
from scoop.messaging.util.signals import thread_created, thread_pre_create, thread_read
from scoop.rogue.models.blocklist import Blocklist


@receiver(thread_pre_create)
def default_pre_thread(sender, author, recipients, request, unique, force, **kwargs):
    """ Traiter la pré-création d'un thread """
    errors = set()
    recipients = make_iterable(recipients)
    # Ne rien faire si le quota de sujets pour user est atteint
    if Quota.objects.exceeded_for(author) and not force:
        errors.add(_("You have started discussions with too much people today."))
    # Ne rien faire s'il n'y a aucun participant ou juste author
    if recipients == {author} or not recipients:
        if not force:
            errors.add(_("Cannot send a new message to nobody."))
    # Vérifier que l'expéditeur n'est pas bloqué par un destinataire
    if getattr(settings, 'MESSAGING_BLACKLIST_ENABLE', False) is True:
        for recipient in recipients:
            if not Blocklist.objects.is_safe(recipient, author):  # or recipient.rule.is_blocked(author):
                errors.add(_("User policy prevents you from talking to at least one recipient."))
    return {'messages': errors} if errors else True


@receiver(thread_created)
def default_post_thread(sender, author, thread, **kwargs):
    """ Traiter la création d'un nouveau thread """
    record.send(None, actor=author, action='messaging.create.thread', target=thread)


@receiver(thread_read)
def default_thread_read(sender, user, thread, **kwargs):
    """ Traiter la lecture d'un thread """
    Recipient.objects.acknowledge(user, thread)
