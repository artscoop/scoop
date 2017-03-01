# coding: utf-8
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import striptags

from scoop.analyze.util.signals import analyzer_default_format
from scoop.content.models.content import Content
from scoop.content.tasks.content import populate_similar
from scoop.content.util.signals import content_format_html
from scoop.core.templatetags.html_tags import truncate_longwords_html
from scoop.core.templatetags.text_tags import truncate_stuckkey
from scoop.core.util.data.textutil import count_words, replace_dict
from scoop.core.util.signals import check_indexable, record


logger = logging.getLogger(__name__)


@receiver(analyzer_default_format)
def auto_format_train_input(sender, value, category, **kwargs):
    """
    Formater le contenu de training de l'analyseur

    :type value: list
    :type category: str
    """
    if isinstance(value, list):
        value = value  # Value est une liste, donc "mutable"
