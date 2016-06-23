# coding: utf-8
from django.apps.registry import apps
from django.contrib.contenttypes.fields import ContentType
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.generic import GenericModel
from scoop.core.abstract.core.uuid import FreeUUIDModel
from scoop.core.util.model.model import SingleDeleteManager


class UUIDEntryManager(SingleDeleteManager):
    """ Manager du registre d'UUID """

    # Getter
    def get_instance(self, uuid):
        entries = self.filter(uuid=uuid)
        if entries.exists():
            return entries[0].content_object
        return None

    # Setter
    def populate(self):
        """ Peupler les UUIDs de tous les modèles """
        modelset = apps.get_models()
        for model in modelset:
            if issubclass(model, FreeUUIDModel):
                with transaction.atomic():
                    entries = model.objects.only('pk', 'uuid').all().iterator()
                    for entry in entries:
                        self.add(entry)

    def clear(self):
        """ Supprimer tous les UUID de tous les modèles """
        self.all().delete()

    def add(self, instance):
        """ Enregistrer un nouvel UUID d'instance """
        if isinstance(instance, FreeUUIDModel):
            content_type = ContentType.objects.get_for_model(instance)
            self.get_or_create(content_type=content_type, object_id=instance.pk, uuid=instance.uuid)

    def remove(self, instance):
        """ Supprimer un UUID du registre """
        self.filter(uuid=instance.uuid).delete()


class UUIDEntry(GenericModel):
    """ Entrée du registre d'UUID """

    # Champs
    uuid = models.CharField(max_length=22, unique=True, blank=False, null=False, verbose_name=_("UUID"))
    objects = UUIDEntryManager()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.uuid

    # Métadonnées
    class Meta:
        verbose_name = _("UUID Reference")
        verbose_name_plural = _("UUID References")
        app_label = 'core'
