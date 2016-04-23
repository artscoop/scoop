# coding: utf-8
from django.dispatch.dispatcher import receiver
from scoop.rogue.util.signals import blocklist_added


@receiver(blocklist_added)
def blocklist_enlisted(sender, user, name, **kwargs):
    """ Un utilisateur a été ajouté à une liste de blocage """
    return None
