# coding: utf-8
from functools import reduce

from annoying.decorators import render_to
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from fuzzywuzzy import fuzz
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.user.ippoint import IPPointableModel, IPPointModel
from scoop.core.templatetags.text_tags import truncate_ellipsis
from scoop.core.util.data.dateutil import now
from scoop.core.util.model.model import SingleDeleteManager, search_query
from scoop.core.util.shortcuts import addattr
from scoop.messaging.util.signals import mailable_event, message_check_spam, message_pre_send, message_sent, message_set_spam
from scoop.messaging.util.text import format_message

__all__ = ['Message']


class MessageManager(SingleDeleteManager):
    """ Manager des messages """

    # Constantes
    MESSAGE_SIZE_LIMIT = 1024

    def get_queryset(self):
        """ Renvoyer le queryset par défaut du manager """
        return super(MessageManager, self).get_queryset()

    # Actions
    def _add(self, thread, author, body, request=None, strip_tags=False, as_mail=True):
        """ Ajouter un message à un fil """
        from scoop.messaging.models import Recipient
        from scoop.user.access.models import IP
        from scoop.user.models import User
        # Par défaut un auteur None devient un bot
        if author is None:
            author = User.objects.get_bot() if (request is None or request.user.is_anonymous()) else request.user
        # Envoyer un signal de vérification
        results = message_pre_send.send(sender=Message, author=author, thread=thread, request=request)
        # Ne rien faire si le traitement l'interdit
        if any([result[1] is not True for result in results]):
            messages = [str(message) for message in reduce(lambda x, y: x + y, [result[1]['messages'] for result in results if result[1] is not True])]
            raise PermissionDenied(", ".join(messages))
        # Formater le corps du message
        body = format_message(body, limit=MessageManager.MESSAGE_SIZE_LIMIT, strip_tags=strip_tags and not request.user.is_staff)
        # Ajouter le message + les indicateurs de non-lecture
        message = Message(thread=thread, author=author, name=author.username, text=body, ip=IP.objects.get_by_request(request))
        message.save(force_insert=True)
        Recipient.objects.set_unread_by_message(message)
        # Envoyer un signal indiquant qu'un message a été envoyé'
        message_sent.send(sender=Message, author=author, message=message, request=request)
        # Récupérer les destinataires
        recipients = thread.get_users(exclude=author)
        # Puis mettre en file des mails à envoyer aux destinataires
        mailtype = 'messaging.message.new' if not author.is_staff else 'messaging.message.staff'
        if as_mail is True and thread.deleted is False:
            for recipient in recipients:
                mailable_event.send(sender=Message, mailtype=mailtype, recipient=recipient, data={'sender': [author], 'message': [message.text]})
        # Mettre à jour la date de mise à jour du sujet
        if not author.is_bot() and author.is_active:
            thread.updater = author
        thread.counter += 1
        thread.save()
        return message

    # Getter
    def for_user(self, user, sorting=None):
        """ Renvoyer les messages à l'attention de l'utilisateur """
        messages = self.select_related('author', 'thread', 'ip').filter(thread__recipient__user=user).exclude(author=user)
        messages = messages.order_by(sorting) if isinstance(sorting, str) else messages
        return messages

    def last_messages(self, minutes=30, **kwargs):
        """ Renvoyer les messages des n dernières minutes """
        stamp = now() - minutes * 60
        messages = self.filter(time__gt=stamp, **kwargs)
        return messages

    def last_user_messages(self, user, minutes=30):
        """ Renvoyer les messages d'un utilisateur pour les n dernières minutes """
        messages = self.last_messages(minutes, author=user)
        return messages

    def user_messages(self, user, **kwargs):
        """ Renvoyer les messages renvoyés par un utilisateur """
        return user.messages_sent.filter(**kwargs)

    def get_last_user_message(self, user, ghost=False):
        """ Renvoyer le dernier message envoyé par un utilisateur """
        filtering = {} if ghost is True else {'deleted': False}
        return user.messages_sent.filter(**filtering).order_by('-id').first()

    def get_user_message_count(self, user, **kwargs):
        """ Renvoyer le nombre de messages envoyés par un utilisateur """
        return user.messages_sent.only('pk').filter(**kwargs).count()

    def text_search(self, expression, **kwargs):
        """ Renvoyer les messages contenant une expression """
        return search_query(expression, ['text'], self.filter(**kwargs))

    def get_spam_data(self, user):
        """ Renvoyer les informations de spam pour un utilisateur """
        data = {'total': self.get_user_message_count(user), '%': 0, 'spam': self.get_user_message_count(user, spam__gt=Message.SPAM_THRESHOLD)}
        data['%'] = (100.0 * data['spam']) / data['total'] if data['total'] > 0 else 0
        return data


class Message(IPPointableModel, DatetimeModel, PicturableModel, DataModel):
    """ Message de discussion """

    # Constantes
    DATA_KEYS = {'pasted', 'similar'}  # clés autorisées par datamodel
    SPAM_THRESHOLD = 0.83

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="messages_sent", on_delete=models.SET_NULL, verbose_name=_("Author"))
    name = models.CharField(max_length=32, verbose_name=_("Name"))
    thread = models.ForeignKey("messaging.Thread", on_delete=models.CASCADE, related_name='messages', null=False, verbose_name=_("Thread"))
    text = models.TextField(blank=False, verbose_name=_("Text"))
    spam = models.FloatField(default=0.0, validators=[MaxValueValidator(1.0), MinValueValidator(0.0)], verbose_name=_("Spam level"))
    deleted = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('message', "Deleted"))
    objects = MessageManager()

    # Getter
    @render_to("messaging/message/body.html")
    def get_text_html(self):
        """ Renvoyer la représentation HTML du message """
        return {'message': self}

    def get_geoip(self):
        """ Renvoyer les informations GeoIP du message """
        return self.ip.get_geoip() if self.ip is not None else None

    def get_recipients(self, only_active=True):
        """ Renvoyer les destinataires du message """
        return self.thread.get_recipients(only_active=only_active)

    def get_recipients_to(self, only_active=True):
        """ Renvoyer les destinataires ciblés par le message """
        return self.thread.get_recipients(exclude=self.author, only_active=only_active)

    def get_similarity(self, message):
        """ Renvoyer l'indice de similarité entre ce message et un autre """
        return fuzz.token_sort_ratio(self.text, message.text)

    def get_similar_user_message_count(self, limit=100, ratio=0.8):
        """ Renvoyer le nombre de messages similaires du même utilisateur """
        messages = Message.objects.user_messages(self.author).order_by('-id')[0:limit]
        return self._get_similar_messages(messages, ratio=ratio)

    def get_similar_message_count(self, minutes=60, limit=100, ratio=0.8):
        """ Renvoyer le nombre de messages similaires de tous les utilisateurs """
        messages = Message.last_messages(minutes=minutes).order_by('-id')[0:limit]
        return self._get_similar_messages(messages, ratio=ratio)

    def check_spam(self):
        """ Vérifier si le message est du spam """
        message_check_spam.send(None, message=self)

    @addattr(boolean=True, short_description=_("Spam"))
    def is_spam(self):
        """ Renvoyer si le message est du spam """
        return self.spam >= Message.SPAM_THRESHOLD

    # Setter
    def set_spam(self, value=None, save=True):
        """ Définir le niveau de spam du message"""
        value = 1.0 if value is None else 0.0 if value < 0 else 1.0 if value > 1 else value
        message_set_spam.send(None, message=self)
        self.update(spam=value, save=save)

    def remove(self):
        """ Supprimer le message """
        self.delete()
        self.thread.delete() if self.thread.counter == 0 else self.thread.save(force_update=True)

    # Privé
    def _get_similar_messages(self, messages, ratio=0.8):
        """ Renvoyer le nombre de messages similaires dans un queryset de messages """
        return len([True for message in messages if self.get_similarity(message) >= ratio])

    @render_to("messaging/message/body-classify.txt")
    def _get_text_classify(self):
        """ Renvoyer une représentation tokenisée du texte de message pour la classification """
        return {'message': self}

    # Propriétés
    recipients = property(get_recipients)
    geoip = property(get_geoip)
    html = property(get_text_html)
    ip_address = property(IPPointModel.get_ip_address, IPPointModel.set_ip)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer le message dans la base de données """
        self.text = self.text.strip()
        if self.name == '' and self.author is not None:
            self.name = self.author.username
        self.check_spam()
        super(Message, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer le message de la base de données """
        if kwargs.pop('clear', False) is True:
            super(Message, self).delete(*args, **kwargs)
        elif self.deleted is False:
            self.thread.counter -= 1
            self.thread.save()
            self.deleted = True
            self.save()
        return True

    def undelete(self):
        """ Restaurer le message si marqué comme supprimé """
        if self.deleted is True:
            self.thread.counter += 1
            self.thread.save()
            self.deleted = False
            self.save()

    def __str__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return """Message #{thread:010} "{message}" """.format(thread=self.thread_id, message=truncate_ellipsis(self.text, 24))

    def get_absolute_url(self):
        """ Renvoyer l'URL de l'objet """
        return self.thread.get_absolute_url()

    # Métadonnées
    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        permissions = (("can_force_send", "Can force send messages"),
                       ("can_broadcast", "Can broadcast messages"),
                       )
        app_label = "messaging"
