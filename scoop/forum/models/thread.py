# coding: utf-8
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.content.subscription import SubscribableModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.util.model.model import SingleDeleteQuerySet
from scoop.core.util.shortcuts import addattr
from scoop.forum.models.label import LabelledModel


class ThreadQuerySet(SingleDeleteQuerySet):
    """ Queryset des fils de discussion publics """

    # Getter
    def visible(self):
        """ Renvoyer les fils visibles """
        return self.filter(visible=True)

    def hidden(self):
        """ Renvoyer les fils invisibles """
        return self.filter(visible=False)

    # Actions
    def new(self, author, subject, body, request=None, closed=False):
        """
        Créer un nouveau fil de discussion avec un message

        :param author: utilisateur ayant créé le fil de discussion
        :param subject: titre du nouveau fil
        :param body: corps du nouveau fil, en HTML
        :param request: objet Request pour afficher des messages d'avertissement si besoin
        :param closed: définit si le sujet doit être fermé dès sa création
        """
        thread = self.create(author=author, updater=author, topic=subject, deleted=False, closed=closed)
        thread.add_message(author, body, request)


class Thread(DatetimeModel, UUID64Model, LabelledModel, DataModel, PicturableModel, SubscribableModel):
    """ Fil de discussion public """

    # Constantes
    DATA_KEYS = ['notes', 'similar_threads']

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='public_threads', verbose_name=_("Author"))
    topic = models.CharField(max_length=128, blank=True, db_index=True, verbose_name=_("Topic"))
    started = models.DateTimeField(default=timezone.now, verbose_name=pgettext_lazy('thread', "Was started"))
    edited = models.DateTimeField(default=None, null=True, verbose_name=pgettext_lazy('thread', "Edited"))
    updated = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=pgettext_lazy('thread', "Updated"))
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='forum_threads_where_last', on_delete=models.SET_NULL,
                                verbose_name=_("Last speaker"))
    deleted = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Deleted"))
    counter = models.IntegerField(default=0, verbose_name=_("Message count"))
    locked = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Locked"))
    sticky = models.BooleanField(default=False, db_index=True, verbose_name=_("Always on top"))
    visible = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Visible"))
    objects = ThreadQuerySet.as_manager()

    # Actions
    def add_message(self, author, body, request):
        """ Ajouter un message au fil de discussion """
        return self.messages._add(self, author, body, request)

    # Getter
    @addattr(short_description=_("All messages"))
    def get_messages(self, ghost=False, reverse=False):
        """ Renvoyer les messages du fil """
        criteria = {'deleted': False} if not ghost else {}
        messages = self.messages.filter(**criteria).order_by('id' if not reverse else '-id')
        return messages

    def get_latest_message(self, ghost=False):
        """ Renvoyer le dernier messages du fil """
        messages = self.get_messages(ghost=ghost, reverse=True)
        if messages.exists():
            return messages.first()
        return None

    @addattr(admin_order_field='counter', short_description=_("Messages"))
    def get_message_count(self, ghost=False, use_cache=False):
        """ Renvoyer le nombre de messages dans le fil """
        return self.counter if use_cache else self.get_messages(ghost=ghost).count()

    def get_participants(self, only_active=True):
        """ Renvoyer les participants à un fil de discussion """
        return self.participants.filter(**({'active': True} if only_active else {}))

    def get_updated(self):
        """ Renvoyer la date de mise à jour (édition ou dernier message) """
        message = self.get_latest_message()
        dates = [self.started]
        if message is not None:
            dates.append(message.get_datetime())
        if self.edited is not None:
            dates.append(self.edited)
        return max(dates)

    # Setter
    def update_message_count(self, save=True):
        """ Mettre à jour le nombre de messages du fil """
        self.counter = self.get_message_count(ghost=False, use_cache=False)
        if save is True:
            self.save(update_fields=['counter'])
        return self.counter

    def lock(self, value=True):
        """
        Verrouiller (déverrouiller) le sujet

        :returns: True si l'état de l'objet a changé, False sinon.
        """
        if self.locked != value:
            self.locked = value
            self.save()
            return True
        return False

    def set_visible(self, value=False):
        """
        Changer la visibilité du sujet

        :returns: True si l'état de l'objet a changé, False sinon.
        """
        if self.visible != value:
            self.visible = value
            self.save()
            return True
        return False

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.updated = self.get_updated()
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

    def get_absolute_url(self):
        """ Renvoyer l'URL du fil """
        return reverse_lazy('forum:thread-view', kwargs={'uuid': self.uuid})

    # Métadonnées
    class Meta:
        verbose_name = _("thread")
        verbose_name_plural = _("threads")
        app_label = 'forum'
