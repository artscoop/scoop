# coding: utf-8
from django.dispatch.dispatcher import receiver
from scoop.content.models.content import Content
from scoop.rogue.util.signals import flag_resolve


@receiver(flag_resolve, sender=Content)
def resolve_content_flag(sender, flag, iteration, **kwargs):
    """ Résoudre automatiquement un flag sur un contenu """
    target = flag.content_object
    # Verrouiller le contenu au bout du 3e flag
    if iteration >= 3:
        target.locked = True
        target.publish_plain(False)
        return True
    return False
