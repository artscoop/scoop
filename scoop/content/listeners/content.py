# coding: utf-8
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import striptags

from scoop.content.models.content import Content
from scoop.content.tasks.content import populate_similar
from scoop.content.util.signals import content_format_html
from scoop.core.templatetags.html_tags import truncate_longwords_html
from scoop.core.templatetags.text_tags import truncate_stuckkey
from scoop.core.util.data.textutil import count_words, replace_dict
from scoop.core.util.signals import check_indexable, record


__all__ = ['auto_manage_content', 'new_content', 'content_indexable']

logger = logging.getLogger(__name__)


@receiver(content_format_html)
def auto_format_content_output(sender, instance, **kwargs):
    """
    Formater le contenu HTML du contenu

    :type instance: scoop.content.models.Content
    """
    replacements = {'**': '\u2731', '--': '\u2e3a', '---': '\u2e3b', '!=': '\u2260', '<=': '\u2264', '>=': '\u2265',
                    '[.]': '\u220e', '...': '\u2026', '!!': '\u203c', '-> ': '\u279c '}
    instance.html = replace_dict(instance.html, replacements)


@receiver(pre_save, sender=Content)
def auto_manage_content(sender, instance, raw, using, update_fields, **kwargs):
    """ Traiter un contenu avant qu'il ne soit sauvegardé """
    instance.body = truncate_stuckkey(instance.body, 3)
    instance.body = truncate_longwords_html(instance.body)
    instance.clean_body()
    return None


@receiver(post_save, sender=Content)
def new_content(sender, instance, raw, created, using, update_fields, **kwargs):
    """ Traiter un contenu qui vient d'être sauvegardé """
    instance.clean_tags()
    instance._populate_html()
    populate_similar.delay(instance)
    try:
        if created:
            author = instance.authors.all().first()
            record.send(None, actor=author, action='content.create.content', target=instance)
    except Content.DoesNotExist as e:
        logger.warning(e)


@receiver(check_indexable, sender=Content)
def content_indexable(sender, instance=None, **kwargs):
    """ Renvoyer su un contenu est indexable par un moteur de recherche """
    text = striptags(instance.body)
    words = count_words(text)
    return words > 299
