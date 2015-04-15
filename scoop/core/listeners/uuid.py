# coding: utf-8
from __future__ import absolute_import

from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from scoop.core.abstract.core.uuid import FreeUUIDModel
from scoop.core.tasks.uuid import remove_uuid_entry, write_uuid_entry

__all__ = ['reference_create', 'reference_remove']


@receiver(post_save, sender=FreeUUIDModel)
def reference_create(sender, instance, raw, created, using, **kwargs):
    """ Ajouter une référence à l'objet UUID """
    if created and isinstance(instance, FreeUUIDModel):
        write_uuid_entry.delay(instance)


@receiver(post_delete, sender=FreeUUIDModel)
def reference_remove(sender, instance, using, **kwargs):
    """ Supprimer la référence à un objet UUID"""
    if isinstance(instance, FreeUUIDModel):
        remove_uuid_entry.delay(instance)
