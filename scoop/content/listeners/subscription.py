# coding: utf-8
import logging

from django.dispatch.dispatcher import receiver
from scoop.content.models.content import Content
from scoop.content.models.subscription import Subscription
from scoop.content.util.signals import content_updated
from scoop.messaging.util.signals import mailable_event

__all__ = []

logger = logging.getLogger(__name__)


@receiver(content_updated)
def send_subscription_notices(sender, instance, **kwargs):
    """ Envoyer les mails pour les abonnés au contenu """
    if isinstance(instance, Content):
        for subscription in Subscription.objects.for_content(instance):
            mailable_event.send(sender=instance, mailtype='content.subscription.update', recipient=subscription.email, data={})
