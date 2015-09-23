# coding: utf-8
from __future__ import absolute_import

import os

from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext, pgettext_lazy

from scoop.content.util.attachment import get_attachment_upload_path
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.fileutil import get_mime_type


class AttachmentManager(SingleDeleteManager):
    """ Manager des pièces jointes """

    # Getter
    def get_link_by_uuid(self, uuid):
        """ Renvoyer un lien HTML vers un fichier portant un UUID spécifique """
        try:
            attachment = self.get(uuid=uuid)
            result = """<a href="{url}">{name}</a>""".format(url=attachment.file.url, name=attachment.get_name())
            return result
        except Attachment.DoesNotExist:
            return ""

    def get_by_object(self, item):
        """ Renvoyer les fichiers joints à un objet """
        content_type = ContentType.objects.get_for_model(item)
        return self.filter(content_type=content_type, object_id=item.pk)

    # Setter
    def attach(self, attachment, target, force=False):
        """ Joindre un fichier à un objet """
        if isinstance(attachment, Attachment) and isinstance(target, models.Model):
            if force is True or attachment.content_object is None:
                attachment.content_object = target
                attachment.save()


class Attachment(DatetimeModel, AuthoredModel, UUID64Model):
    """ Pièce jointe fichier """
    # Champs
    group = models.CharField(max_length=16, blank=True, db_index=True, verbose_name=_("Group"))
    file = models.FileField(max_length=192, upload_to=get_attachment_upload_path, verbose_name=_("File"), help_text=_("File to attach"))
    name = models.CharField(max_length=64, blank=True, verbose_name=_("Name"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))
    mimetype = models.CharField(max_length=40, blank=True, verbose_name=_("MIME type"))
    limit = models.Q(model__in={'Profile', 'Content'})  # limite des content types
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, related_name='attachments', limit_choices_to=limit, verbose_name=_("Content type"))
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True, verbose_name=_("Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    objects = AttachmentManager()

    # Getter
    @addattr(boolean=True, short_description=_("Valid"))
    def exists(self):
        """ Renvoyer si le fichier existe """
        return self.id and self.file and self.file.path and os.path.exists(self.file.path)

    @addattr(allow_tags=True, short_description=_("Link"))
    def get_link(self):
        """ Renvoyer un lien HTML vers le fichier """
        return Attachment.objects.get_link_by_uuid(self.uuid)

    @addattr(short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom du fichier """
        return os.path.basename(self.file.name)

    @addattr(short_description=_("Size"))
    def get_file_size(self):
        """ Renvoyer la taille du fichier au format lisible """
        if self.exists():
            return filesizeformat(self.file.size)
        else:
            return pgettext('size', "None")

    @addattr(boolean=True, short_description=pgettext_lazy('attachment', "Orphaned"))
    def is_orphan(self):
        """ Renvoyer si la pièce jointe n'a pas de cible """
        return self.content_object is None

    # Setter
    def update_path(self):
        """ Déplacer le fichier vers son chemin par défaut """
        new_path = get_attachment_upload_path(self, "", update=True)
        filename = self.get_filename()
        output = os.path.join(settings.MEDIA_ROOT, new_path, filename)
        output_file = os.path.join(new_path, filename)
        os.renames(self.file.path, output)
        # Recréer l'image depuis le nouveau chemin
        self.file = output_file
        self.save()

    def detach(self):
        """ Détacher la pièce jointe de sa cible """
        self.content_object = None
        self.save()

    def set_mime_auto(self, save=False):
        """ Détecter et définir le type MIME du fichier """
        if self.mimetype == "":
            try:
                self.mimetype = get_mime_type(self.file.path)
                if save is True:
                    self.save()
            except:
                self.mimetype = 'application/octet-stream'

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "{}".format(self.file.name)

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.set_mime_auto(save=False)
        super(Attachment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.file.delete()
        super(Attachment, self).delete(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        permissions = (("can_join_files", "Can join files"),)
        app_label = "content"
