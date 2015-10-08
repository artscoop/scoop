# coding: utf-8
from __future__ import absolute_import

import logging

from django.apps import apps
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver

from scoop.content.models.comment import Comment
from scoop.content.models.content import Content
from scoop.content.tasks.content import populate_similar
from scoop.content.util.signals import comment_posted, content_updated
from scoop.core.templatetags.html_tags import truncate_longwords_html
from scoop.core.templatetags.text_tags import truncate_stuckkey
from scoop.core.util.signals import check_indexable, record
from scoop.forum.models.read import Read

__all__ = []

logger = logging.getLogger(__name__)


@receiver(comment_posted, sender=Comment)
def new_comment(sender, target, **kwargs):
    """ Traiter un nouveau commentaire """
    if isinstance(target, Content):
        content_updated.send(instance=target)
