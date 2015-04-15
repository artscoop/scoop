# coding: utf-8
from django.dispatch.dispatcher import receiver

from scoop.core.util.signals import record
from scoop.rogue.util.signals import flag_created


@receiver(flag_created)
def flag_creation(sender, flag, **kwargs):
    """ Consigner la création d'un nouveau signalement """
    if sender.author is not None:
        record.send(None, actor=flag.author, action='rogue.create.flag', target=flag.content_object)
