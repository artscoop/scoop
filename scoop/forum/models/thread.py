# coding: utf-8
from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.forum.models.label import LabelledModel


class Thread(DatetimeModel, UUID64Model, LabelledModel):

    # Constantes
    DATA_KEYS = ['notes']

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='public_threads', verbose_name=_("Author"))
    topic = models.CharField(max_length=128, blank=True, db_index=True, verbose_name=_("Topic"))
    started = models.DateTimeField(default=timezone.now, verbose_name=pgettext_lazy('thread', "Was started"))
    updated = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=pgettext_lazy('thread', "Updated"))
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='forum_threads_where_last', on_delete=models.SET_NULL, verbose_name=_("Last speaker"))
    deleted = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Deleted"))
    counter = models.IntegerField(default=0, verbose_name=_("Message count"))
    locked = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Locked"))
    sticky = models.BooleanField(default=False, db_index=True, verbose_name=_("Always on top"))
    visible = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Visible"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.updated = timezone.now()
        self.update_message_count(save=False)
        super(Thread, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if kwargs.get('clear', False):
            super(Thread, self).delete(*args, **kwargs)
        else:
            self.deleted = True
            self.save(force_update=True, update_fields=['deleted', 'updated'])
            self.get_messages().update(deleted=True)

    def __str__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return self.topic

    @permalink
    def get_absolute_url(self):
        """ Renvoyer l'URL du fil """
        return 'forum:thread-view', [], {'uuid': self.uuid}

    # Métadonnées
    class Meta:
        verbose_name = _("thread")
        verbose_name_plural = _("threads")
        app_label = 'forum'
