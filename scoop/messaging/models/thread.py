# coding: utf-8
import datetime
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, permalink
from django.db.models.aggregates import Count
from django.http.response import Http404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.util.data.dateutil import to_timestamp
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.django.templateutil import render_block_to_string
from scoop.core.util.model.model import SingleDeleteQuerySetMixin
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.request import default_context
from scoop.messaging.models.label import LabelableModel
from scoop.messaging.util.signals import thread_created, thread_pre_create

logger = logging.getLogger(__name__)

__all__ = ['Thread', 'ThreadManager']


class ThreadQuerySetMixin(object):
    """ Mixin Queryset/MAnager des fils de discussion """

    # Getter
    def by_request(self, request):
        """ Renvoyer les threads non supprimés """
        return self.filter(deleted=False) if (request and not request.user.is_staff) else self

    def deleted(self, **kwargs):
        """ Renvoyer les sujets effacés """
        return self.filter(deleted=True, **kwargs)

    def closed(self, **kwargs):
        """ Renvoyer les sujets fermés """
        return self.filter(closed=True, **kwargs)

    def visible(self, **kwargs):
        """ Renvoyer les sujets visibles """
        return self.filter(deleted=False, closed=False)

    def user_threads(self, user):
        """ Renvoyer les sujets où participe un utilisateur """
        threads = self.filter(recipients__user=user).order_by('-updated')
        return threads

    def user_thread_count(self, user):
        """ Renvoyer le nombre de sujets auxquels participe l'utilisateur """
        return self.user_threads(user).count()

    def user_active_threads(self, user):
        """ Renvoyer les sujets actifs où participe l'utilisateur """
        threads = self.filter(recipients__user=user, recipients__active=True, deleted=False).order_by('-updated')
        return threads

    def user_active_thread_count(self, user):
        """ Renvoyer le nombre de sujets actifs pour l'utilisateur """
        return self.user_active_threads(user).count()

    def related_recipients(self, user, ack=False):
        """ Renvoyer les objets destinataires participant aux mêmes sujets que l'utilisateur """
        from scoop.messaging.models.recipient import Recipient
        # Uniquement les personnes qui ont connaissance de l'existence du fil
        criteria = {'acknowledged': True} if ack else {}  # si ack, uniquement les membres qui ont pris connaissance du contenu 1 fois
        return Recipient.objects.filter(thread__recipients__user=user, **criteria).exclude(user=user)

    def related_users(self, user, ack=False):
        """ Renvoyer les utilisateurs participant aux mêmes sujets que l'utilisateur """
        criteria = {'user_recipients__acknowledged': True} if ack else {}  # si ack, uniquement les membres qui ont pris connaissance du contenu 1 fois
        return get_user_model().objects.filter(user_recipients__thread__recipients__user=user, **criteria).exclude(id=user.id).distinct()

    def get_replied_thread_count(self, user):
        # Renvoyer le nombre de fils dans lesquels l'utilisateur a répondu au moins une fois
        return self.filter(recipients__user=user, messages__author=user).exclude(author=user).distinct().count()

    def get_ignored_thread_count(self, user):
        """ Renvoyer le nombre de fils lus par l'utilisateur mais restés sans réponse """
        result = self.annotate(message_count=Count('messages')).filter(recipients__user=user, recipients__unread=False, message_count=1).exclude(author=user)
        return result.count()

    def unreplied_threads(self, user):
        """ Renvoyer les sujets créés par utilisateur sans aucune réponse """
        return self.filter(author=user, counter=1)

    def closed_threads(self, user):
        """ Renvoyer les sujets fermés d'un utilisateur """
        return self.filter(recipients__user=user, closed=True)

    def threads_not_updated_by(self, user):
        """ Renvoyer les sujets où l'utilisateur n'est pas le dernier à avoir parlé """
        return self.filter(recipients__user=user).exclude(updater=user).distinct()

    def get_unreplied_thread_count(self, user):
        """ renvoyer le nombre de fils créés par un utilisateur et sans réponse """
        return self.unreplied_threads(user).count()

    def unread_threads(self, user, active_only=False):
        """ Renvoyer les fils non lus par un utilisateur """
        queryset = self.filter(recipients__user=user, recipients__unread=True)
        queryset = queryset.user_active_threads(user) if active_only else queryset
        return queryset

    def read_threads(self, user, active_only=False):
        """ Renvoyer les fils lus par un utilisateur """
        queryset = self.filter(recipients__user=user, recipients__unread=False)
        queryset = queryset.user_active_threads(user) if active_only else queryset
        return queryset

    def get_read_thread_count(self, user, active_only=False):
        """ Renvoyer le nombre de fils lus par un utilisateur """
        return self.read_threads(user, active_only=active_only).count()

    def get_created_thread_count(self, user):
        """ Renvoyer le nombre de fils créés par un utilisateur """
        total = self.filter(author=user).count()
        return total

    def common_threads(self, *users, **kwargs):
        """ Renvoyer les fils communs à plusieurs utilisateurs """
        threads = self.filter(**kwargs)
        for user in users:
            threads = threads.filter(recipients__user=user)
        return threads

    def get_common_thread_count(self, *users, **kwargs):
        """ Renvoyer le nombre de fils communs à plusieurs utilisateurs """
        return self.common_threads(*users, **kwargs).count()

    def get_user_threads_message_count(self, user, **kwargs):
        """ Renvoyer le nombre de messages envoyés par sujet par un utilisateur """
        from scoop.messaging.models import Recipient
        data = Recipient.objects.filter(user=user, **kwargs).values('thread_id', 'thread__updated', 'thread__deleted',
                                                                    'thread__updater', 'thread__closed', 'counter')
        return data

    def get_by_uuid(self, uuid, exception=Http404):
        """ Renvoyer un fil par UUID ou renvoyer une exception """
        try:
            return self.get(uuid=uuid)
        except Thread.DoesNotExist:
            raise exception()

    def by_recipient_count(self, count, modifier=None, **kwargs):
        """
        Renvoyer les fils ayant un nombre de destinataires
        :param modifier: ex. 'gt', 'lt', 'gte' etc.
        """
        criteria = {'population__{}'.format(modifier): count} if modifier else {'population': count}
        kwargs.update(criteria)
        return self.filter(**kwargs)

    def get_inbox(self, user, name=None):  # name: [inbox|unread|replied|trash]
        """
        Renvoyer les informations d'une boîte de réception

        :param name: nom de la boîte de messagerie, entre :
            - inbox : boîte contenant tous les fils de discussion
            - unread : boîte contenant les fils de discussion avec des messages non lus
            - replied : boîte contenant les fils de discussion où une réponse est attendue
            - trash : boîte contenant les fils de discussion supprimés par user
            Si name est `None`, inbox est utilisé par défaut.
            Si un nom inconnu est utilisé, aucun thread n'est renvoyé
        :type name: str | None
        """
        name = name or "inbox"
        groups = {'inbox': self.user_active_threads(user),
                  'unread': self.unread_threads(user),
                  'replied': self.threads_not_updated_by(user),
                  'trash': Thread.objects.closed().user_threads(user)}
        titles = {'inbox': _("Inbox"),
                  'unread': _("Unread threads"),
                  'replied': _("Waiting for your reply"),
                  'trash': _("Trash")}
        return {'title': titles.get(name, ""), 'threads': groups.get(name, self.none())}

    def get_inbox_names(self):
        """ Renvoyer les noms des boîtes de réception """
        return Thread.INBOX_NAMES

    # Setter
    def delete_batch(self, days=90, deleted=True, clear=True):
        """ Supprimer des fils de discussion plus vieux que n jours """
        limit = datetime.date.today() - datetime.timedelta(days=days)
        threads = self.filter(updated__lt=limit)
        if deleted:
            threads = threads.filter(Q(deleted=True) | Q(closed=True))
        count = threads.count()
        for thread in threads:
            thread.delete(clear=clear)
        return count


class ThreadQuerySet(models.QuerySet, ThreadQuerySetMixin, SingleDeleteQuerySetMixin):
    """ Queryset des fils de discussion """
    pass


class ThreadManager(models.Manager.from_queryset(ThreadQuerySet), models.Manager, SingleDeleteQuerySetMixin, ThreadQuerySetMixin):
    """ Manager des fils de discussion """

    # Actions
    def new(self, author, recipients, subject, body, request=None, closed=False, unique=None, as_mail=True, force=False, expiry=None):
        """
        Créer un nouveau fil de discussion

        :param author: utilisateur ayant créé le fil de discussion
        :param recipients: liste des utilisateurs destinataires du message
        :param subject: titre du nouveau fil
        :param body: corps du nouveau fil, en HTML
        :param request: objet Request pour afficher des messages d'avertissement si besoin
        :param closed: définit si le sujet doit être fermé dès sa création
        :param unique: définit si le message doit réutiliser un sujet existant avec les mêmes destinataires
        :param as_mail: définit si le message à envoyer provoque l'envoi d'un nouveau mail (selon conditions)
        :param force: définit si un message envoyé à soi-même peur être envoyé
        :param expiry: définit la date à laquelle le sujet va expirer
        :returns: un dictionnaire avec les clés thread, message et created. Ou False en cas d'échec.
        :rtype: dict | bool
        """
        from scoop.messaging.models import Message, Recipient
        # Convertir les destinataires en liste si besoin
        recipients = make_iterable(recipients, set)
        # Pré-creation du thread
        result = thread_pre_create.send(sender=Thread, author=author, recipients=recipients, request=request, unique=unique, force=force)
        # Ne poursuivre que si le traitement a renvoyé True partout
        for value in result:
            if isinstance(value[1], dict):
                messageset = value[1].get('messages', None)
                if len(messageset) > 0 and request is not None:
                    for message in messageset:
                        messages.warning(request, message)
                return False
        # Ajouter l'auteur aux participants
        if author not in recipients:
            recipients.add(author)
        # Créer le sujet ou récupérer un sujet existant, si unique=True
        thread = None
        created = False
        unique = getattr(settings, 'MESSAGING_THREAD_UNIQUE', True) if unique is None else unique
        if unique is True:
            threads = self.filter(closed=False, deleted=False)
            for recipient in recipients:
                threads = threads.filter(recipients__user=recipient)
            if threads.exists():
                for item in threads:
                    if not item.is_staff():
                        thread = item
                        break
                if thread is None:
                    thread = threads[0]
                created = False
                logger.info("Duplicates disabled, message added to thread with identifier {uuid}".format(uuid=thread.uuid))
        if thread is None:
            thread = super(self.__class__, self).create(author=author, updater=author, topic=subject, deleted=False, closed=closed, expires=expiry)
            created = True
            thread_created.send(sender=thread, author=author, thread=thread)
            logger.debug("A new thread with identifier {uuid} has been created".format(uuid=thread.uuid))
            # Ajouter les participants
            thread.add_recipients(recipients)
        # Ack auteur
        Recipient.objects.acknowledge(author, thread)
        # Ajouter le corps du message au sujet, si fourni
        message = Message.objects._add(thread, author, body, request, as_mail=as_mail) if body is not None else None
        return {'thread': thread, 'message': message, 'created': created}

    def open_warning(self, recipients, name="warning", as_mail=True, **kwargs):
        """ Créer un nouveau fil administration via un template """
        if not isinstance(recipients, list):
            recipients = [recipients]
        title, text = [render_block_to_string("messaging/warning/{}.html".format(name), label, kwargs) for label in ['title', 'text']]
        author = getattr(get_user_model().objects, 'get_bot_or_admin')()
        thread = self.new(author, recipients, title, text, closed=True, as_mail=as_mail)
        return {'thread': thread}

    def simulate(self, author, recipients, unique=True, force=False, **kwargs):
        """
        Simuler l'envoi d'un fil de discussion.

        :returns: True si le message peut être envoyé, False sinon.
        :rtype: bool
        """
        result = thread_pre_create.send(sender=Thread, author=author, recipients=recipients, request=None, unique=unique, force=force)
        for value in result:
            if value[1] is not True:
                return False
        return True


class Thread(UUID64Model, LabelableModel, DataModel):
    """ Fil de discussion """
    # Constantes
    CACHE_KEY = {'unread': 'messaging.thread.unread.{}'}
    INBOX_NAMES = ['inbox', 'unread', 'replied', 'trash']
    DATA_KEYS = ['last_toggle']
    TOGGLE_DELAY = getattr(settings, 'MESSAGING_THREAD_TOGGLE_DELAY', 3600)

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='threads', verbose_name=_("Author"))
    topic = models.CharField(max_length=128, blank=True, db_index=True, verbose_name=_("Topic"))
    started = models.DateTimeField(default=timezone.now, verbose_name=pgettext_lazy('thread', "Was started"))
    updated = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=pgettext_lazy('thread', "Updated"))
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='threads_where_last', on_delete=models.SET_NULL, verbose_name=_("Last speaker"))
    deleted = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Deleted"))
    counter = models.IntegerField(default=0, verbose_name=_("Message count"))
    population = models.IntegerField(default=0, verbose_name=_("Recipient count"))
    closed = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('thread', "Closed"))
    # Expiration du sujet : Temps après dernier update avant suppression du message.
    expires = models.DateTimeField(null=True, blank=True, verbose_name=_("Expires"))
    expiry_on_read = models.SmallIntegerField(default=365, help_text=_("Value in days"), verbose_name=_("Expiry on read"))
    objects = ThreadManager()

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
        return ('messaging:thread-view', [], {'uuid': self.uuid})

    # Actions
    def add_message(self, author, body, request=None, strip_tags=False, as_mail=True):
        """ Ajouter un message au fil """
        from scoop.messaging.models import Message
        # Ajouter le message
        return Message.objects._add(self, author, body, request, strip_tags, as_mail)

    def add_bot_message(self, template, as_mail=True, data=None):
        """ Ajouter un message template d'un bot au fil """
        from scoop.messaging.models import Message
        # Ajouter le message
        data = data or dict()
        data.update({'thread': self})
        body = render_to_string("messaging/message/bot/{0}.html".format(template), data, context_instance=default_context())
        return Message.objects._add(self, None, body, None, strip_tags=False, as_mail=as_mail)

    def add_recipients(self, recipients):
        """ Ajouter des destinataires au fil """
        from scoop.rogue.models import Blocklist
        # Vérifier la possibilité d'ajouter chaque destinataire
        recipients = make_iterable(recipients, set)
        for recipient in recipients:
            if Blocklist.objects.is_safe(self.author, recipient):
                recipient, created = self.recipients.get_or_create(thread=self, user=recipient)
                if not created:
                    if not recipient.active:
                        recipient.enable()
                else:
                    self.population += 1
        self.save()

    def remove_recipient(self, user):
        """ Supprimer un destinataire du fil """
        for recipient in self.recipients.filter(user=user, thread=self):
            recipient.disable()
        # Fermer ou supprimer si plus assez de participants
        count = self.get_recipient_count()
        actions = {0: (lambda t: t.delete()), 1: (lambda t: t.toggle(force_close=True))}
        actions.get(count, lambda t: t)(self)

    def remove_all_recipients(self):
        """ Supprimer tous les destinataires du fil """
        for recipient in self.recipients.all():
            recipient.disable()
        self.population = 0
        self.save()

    # Setter
    def set_closed(self, closed, actor=None):
        """ Fermer ou ouvrir le fil si possible """
        if actor is None or actor.is_staff or (self.author == actor and self.can_be_toggled(actor)):
            closed = not self.closed if closed is None else closed  # closed = None équivaut à un toggle
            if self.closed != closed:
                self.closed = closed
                self.set_data('last_toggle', timezone.now(), save=True)
                return True
        return False

    def truncate(self, count=40):
        """ Réduire le nombre de messages du fil à un nombre prédéfini """
        try:
            messages = self.messages.filter(deleted=False).order_by('-id')
            messages = messages[count:]
            [message.remove() for message in messages]
            return True
        except Exception:
            return False

    def update_message_count(self, save=True):
        """ Mettre à jour le nombre de messages du fil """
        self.counter = self.get_message_count(ghost=False, use_cache=False)
        if save is True:
            self.save(update_fields=['counter'])
        return self.counter

    def update_recipient_count(self):
        """ Mettre à jour le nombre de destinataires du fil """
        self.population = self.recipients.filter(active=True, user__is_active=True).count()
        self.save()
        return self.population

    def undelete(self):
        """ « Désupprimer » le fil """
        if self.deleted is True:
            self.deleted = False
            self.save()
            return True
        return False

    def set_expiry(self, days=60, override=False):
        """ Définir la date d'expiration du fil """
        if days > 0 and (override or self.expires is None):
            expiry = timezone.now() + datetime.timedelta(days=days)
            self.expires = expiry
            self.save(update_fields=['expires'])
        elif days is None and self.expiry_on_read > 2:
            self.set_expiry(days=self.expiry_on_read, override=True)

    def remove_expiry(self, permanent=False):
        """ Supprimer la date d'expiration du fil """
        self.expires = None
        if permanent:
            self.expiry_on_read = 0
        self.save(update_fields=['expires', 'expiry_on_read'])

    # Getter
    @addattr(short_description=_("Topic"))
    def get_topic(self):
        """ Renvoyer le sujet du fil """
        return self.topic or mark_safe(render_to_string('messaging/message/subject/no-subject.txt', {'thread': self}))

    @addattr(short_description=_("All messages"))
    def get_messages(self, ghost=False, reverse=False):
        """ Renvoyer les messages du fil """
        criteria = {'deleted': False} if not ghost else {}
        messages = self.messages.filter(**criteria).order_by('id' if not reverse else '-id')
        return messages

    @addattr(short_description=_("Last message"))
    def get_last_message(self, ghost=False):
        """ Renvoyer le dernier message du sujet """
        messages = self.get_messages(ghost=ghost).order_by('-id')
        return messages[0]

    @addattr(short_description=_("First message"))
    def get_first_message(self, ghost=False):
        """ Renvoyer le premier message du sujet """
        messages = self.get_messages(ghost=ghost).order_by('id')
        return messages[0]

    @addattr(short_description=_("Recipients"))
    def get_recipients(self, exclude=None, only_active=True):
        """ Renvoyer les objets Recipient du fil """
        criteria = {'active': True} if only_active else {}
        exclusion = {'id__in': map(lambda i: i.id, make_iterable(exclude))} if exclude else {}
        recipients = self.recipients.select_related('user', 'user__profile__picture').filter(**criteria).exclude(**exclusion)
        return recipients

    def get_recipient(self, user):
        """ Renvoyer l'objet Recipient d'un utilisateur pour le fil """
        recipients = self.recipients.filter(user=user)
        return recipients[0] if recipients.exists() else None

    def get_talking_users(self, exclude_staff=False):
        """ Renvoyer la liste des utilisateurs qui ont participé au sujet, même les non destinataires """
        criteria = {'is_staff': False, 'bot': False} if exclude_staff else {}
        return get_user_model().objects.filter(messages_sent__thread=self, **criteria).distinct()

    @addattr(short_description=_("Users"))
    def get_users(self, exclude=None, only_active=True):
        """ Renvoyer les utilisateurs participant au fil """
        criteria = {'user_recipients__active': True} if only_active else {}
        exclusion = {'id__in': map(lambda i: i.id, make_iterable(exclude))} if exclude else {}
        users = get_user_model().objects.filter(user_recipients__thread=self, **criteria).exclude(**exclusion).distinct()
        return users

    @addattr(admin_order_field='population', short_description=_("Recipients"))
    def get_recipient_count(self, only_active=True):
        """ Renvoyer le nombre de participants au fil """
        recipients = self.get_recipients(only_active=only_active)
        return recipients.count()

    def is_recipient(self, user):
        """ Renvoyer si un utilisateur participe actuellement au fil """
        exists = self.recipients.filter(user=user, active=True).exists()
        return user.is_staff or getattr(user, 'bot', False) or exists

    def is_recipient_or_raise(self, user, exception):
        """ Renvoyer si un utilisateur participe au fil ou lever une exception """
        if not self.is_recipient(user):
            raise exception()

    @addattr(admin_order_field='counter', short_description=_("Messages"))
    def get_message_count(self, ghost=False, use_cache=False):
        """ Renvoyer le nombre de messages dans le fil """
        return self.counter if use_cache else self.get_messages(ghost=ghost).count()

    def get_user_message_count(self, user, ghost=False):
        """ Renvoyer le nombre de messages postés par un utilisateur dans le fil """
        filtering = {} if ghost else {'deleted': False}
        total = self.messages.filter(author=user, **filtering).count()
        return total

    @addattr(boolean=True, short_description=_("Unread"))
    def is_unread(self, user):
        """ Renvoyer si un utilisateur n'a pas lu le fil """
        from scoop.messaging.models import Recipient
        # Renvoyer l'état
        return Recipient.objects.is_unread(self, user)

    @addattr(boolean=True, short_description=_("All read"))
    def is_read_by_everyone(self):
        """ Renvoyer si tous les participants ont lu le fil """
        return not self.recipients.filter(unread=True).exists()

    @addattr(boolean=True, short_description=_("Staff thread"))
    def is_staff(self):
        """ Renvoyer si l'auteur du sujet fait partie du personnel """
        return self.author.is_staff or self.author.is_superuser

    @addattr(short_description=_("Unread count"))
    def get_unread_count(self, since=None):
        """ Renvoyer le nombre de destinataires n'ayant pas lu le fil """
        filtering = {} if since is None else {'time__gt': to_timestamp(since)}
        unread = self.recipients.filter(unread=True, **filtering).count()
        return unread

    def has_blacklist(self, user):
        """ Renvoyer si un utilisateur est blacklisté par un destinataire du fil """
        from scoop.rogue.models import Blocklist
        # Via blocklist.blacklist
        recipients = self.get_users(exclude=user)
        return not Blocklist.objects.is_safe(user, recipients)

    def get_toggle_lock_remaining(self, user):
        """ Renvoyer le temps que doit attendre un utilisateur avant de pouvoir rouvrir ou refermer un sujet """
        if user == self.author and not user.is_staff:
            difference = self.get_data('last_toggle', self.started) + timedelta(seconds=Thread.TOGGLE_DELAY) - timezone.now()
            return difference if difference.total_seconds() > 0 else None
        return None

    def can_be_toggled(self, user):
        """ Renvoyer si l'utilisateur peut basculer l'état de fermeture du fil """
        if user.is_staff:
            return True
        return False if self.get_toggle_lock_remaining(user) else True

    # Métadonnées
    class Meta:
        verbose_name = _("thread")
        verbose_name_plural = _("threads")
        app_label = "messaging"
