# coding: utf-8
import logging

from django.apps import apps
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from scoop.content.models.content import Content
from scoop.content.tasks.content import populate_similar
from scoop.core.templatetags.html_tags import truncate_longwords_html
from scoop.core.templatetags.text_tags import truncate_stuckkey
from scoop.core.util.signals import check_indexable, record
from scoop.forum.models.read import Read

__all__ = ['auto_manage_content', 'new_content', 'content_indexable']

logger = logging.getLogger(__name__)


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
        elif apps.is_installed('scoop.forum'):
            Read.objects.unset(instance)
    except Content.DoesNotExist as e:
        logger.warning(e)


@receiver(check_indexable, sender=Content)
def content_indexable(sender, instance=None, **kwargs):
    """ Renvoyer su un contenu est indexable par un moteur de recherche """
    # TODO: Vérifier le contenu etc.
    return False
