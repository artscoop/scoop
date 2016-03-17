# coding: utf-8
import logging

from django.dispatch.dispatcher import receiver
from scoop.content.models.content import Content
from scoop.content.util.signals import comment_posted, content_updated

__all__ = []

logger = logging.getLogger(__name__)


@receiver(comment_posted, sender=Content)
def new_comment_on_content(sender, target, **kwargs):
    """ Traiter un nouveau commentaire dans un contenu """
    content_updated.send(instance=target)
