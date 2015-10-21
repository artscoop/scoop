# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.signals import record


class LikeManager(SingleDeleteManager):
    """ Manager des likes """

    # Getter
    def exists(self, item, author):
        """ Renvoyer si un utilisateur a liké un objet """
        item_type = ContentType.objects.get_for_model(item)
        return self.filter(author=author, content_type=item_type, object_id=item.pk).exists()

    # Setter
    def like(self, item, author):
        """ Liker un objet """
        if author:
            item_type = ContentType.objects.get_for_model(item)
            _, created = self.get_or_create(author=author, content_type=item_type, object_id=item.pk)
            if created is True:
                record.send(None, actor=author, action='social.like', target=item)
            return created
        return False

    def unlike(self, item, author):
        """ Ne plus liker un objet """
        if author:
            item_type = ContentType.objects.get_for_model(item)
            deleted_count = self.filter(author=author, content_type=item_type, object_id=item.pk).delete()
            if deleted_count > 0:
                record.send(None, actor=author, action='social.unlike', target=item)
                return True
        return False

    def toggle(self, item, author):
        """ Basculer un like à un objet """
        if author and item:
            if self.exists(item, author):
                self.unlike(item, author)
                return False
            else:
                self.like(item, author)
                return True
        return None

    def reset_on(self, item):
        """ Supprimer tous les likes d'un objet """
        if item is not None:
            item_type = ContentType.objects.get_for_model(item)
            return self.filter(content_type=item_type, object_id=item.pk).delete() > 0
        return False


class Like(DatetimeModel):
    """ Annotation "J'aime" sur un objet arbitraire. """
    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='likees', verbose_name=_("Author"))
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=False, verbose_name=_("Content type"), limit_choices_to={'app_label__in': ['content']})
    object_id = models.PositiveIntegerField(null=True, blank=False, verbose_name=_("Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    objects = LikeManager()

    # Overrides
    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.content_type = None
        self.object_id = None
        super().delete(*args, **kwargs)

    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{user} likes {target}").format(user=self.author.username, target=self)

    # Métadonnées
    class Meta:
        verbose_name = _("like")
        verbose_name_plural = _("likes")
        unique_together = (('author', 'content_type', 'object_id'),)
        app_label = 'social'
