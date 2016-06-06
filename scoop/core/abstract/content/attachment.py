# coding: utf-8

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AttachableModel(models.Model):
    """ Objet pouvant être lié à des fichiers via une relation générique """

    # Champs
    has_attachments = models.BooleanField(default=False, db_index=True, verbose_name=_("\U0001f58c"))
    attachments = GenericRelation('content.attachment')

    # Getter
    def get_attachment_count(self):
        """ Renvoyer le nombre de fichiers joints """
        return self.attachments.count()

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.has_attachments = self.attachments.exists()
        super(AttachableModel, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        abstract = True
