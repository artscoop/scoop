# coding: utf-8
from __future__ import absolute_import

from django.dispatch.dispatcher import receiver

from scoop.rogue.util.signals import flag_resolve


@receiver(flag_resolve)
def resolve_content_flag(sender, iteration, **kwargs):
    """ Résoudre automatiquement un flag sur un contenu """
    target = sender.content_object
    content_type = sender.content_type.model
    app_label = sender.content_type.app_label
    # Verrouiller le contenu au bout du 3e flag
    if (app_label, content_type) == ('content', 'content'):
        if iteration == 3:
            target.locked = True
            target.publish_plain(False)
        return True
    return False
