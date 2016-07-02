# coding: utf-8
from celery import task


@task(name='core.add_uuid', ignore_result=True, expires=60)
def write_uuid_entry(instance):
    """ Consigner un nouvel UUID """
    from scoop.core.abstract.core.uuid import FreeUUIDModel
    from scoop.core.models.uuidentry import UUIDEntry
    # Vérifier le type de l'objet
    if isinstance(instance, FreeUUIDModel):
        UUIDEntry.objects.add(instance)


@task(name='core.remove_uuid', ignore_result=True, expires=60)
def remove_uuid_entry(instance):
    """ Retirer un UUID du registre """
    from scoop.core.abstract.core.uuid import FreeUUIDModel
    from scoop.core.models.uuidentry import UUIDEntry
    # Vérifier le type de l'objet
    if isinstance(instance, FreeUUIDModel):
        UUIDEntry.objects.remove(instance)
