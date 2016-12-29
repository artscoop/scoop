# coding: utf-8

from django.conf import settings
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from fuzzywuzzy import fuzz

from scoop.analyze.abstract.classifiable import ClassifiableModel
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.user.ippoint import IPPointableModel, IPPointModel
from scoop.core.templatetags.text_tags import truncate_ellipsis
from scoop.core.util.data.dateutil import now
from scoop.core.util.django.templateutil import do_render
from scoop.core.util.model.model import SingleDeleteManager, search_query


__all__ = ['Message']


class MessageManager(SingleDeleteManager):
    """ Manager des messages """

    # Constantes
    MESSAGE_SIZE_LIMIT = 1024

    def get_queryset(self):
        """ Renvoyer le queryset par défaut du manager """
        return super(MessageManager, self).get_queryset()

    # Getter
    def for_user(self, user, sorting=None):
        """ Renvoyer les messages à l'attention de l'utilisateur """
        messages = self.select_related('author', 'thread', 'ip').filter(thread__participant__user=user).exclude(author=user)
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

    # Actions
    def _add(self, thread, author, body, request):
        # Par défaut un auteur None devient un bot
        from scoop.user.models import User
        from scoop.user.access.models import IP
        if author is None:
            author = User.objects.get_bot() if (request is None or request.user.is_anonymous()) else request.user
        # Ajouter le message + les indicateurs de non-lecture
        message = Message(thread=thread, author=author, name=author.username, text=body, ip=IP.objects.get_by_request(request))
        message.save(force_insert=True)


class Message(IPPointableModel, DatetimeModel, PicturableModel, DataModel, ClassifiableModel):
    """ Message de discussion publique """

    # Constantes
    DATA_KEYS = {'pasted', 'similar'}  # clés autorisées par datamodel
    classifications = {'spam': ['y', 'n']}

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="forum_messages_sent", on_delete=models.SET_NULL, verbose_name=_("Author"))
    name = models.CharField(max_length=32, verbose_name=_("Name"))
    thread = models.ForeignKey("forum.Thread", on_delete=models.CASCADE, related_name='messages', null=False, verbose_name=_("Thread"))
    text = models.TextField(blank=False, verbose_name=_("Text"))
    deleted = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('message', "Deleted"))
    objects = MessageManager()

    # Getter
    def get_text_html(self, request):
        """
        Renvoyer la représentation HTML du message

        :param request: requête Http
        """
        return do_render(request, "forum/message/body.html", {'message': self}, string=True)

    def get_document(self):
        """ Renvoyer le contenu à classifier """
        return self.text

    def get_geoip(self):
        """ Renvoyer les informations GeoIP du message """
        return self.ip.get_geoip() if self.ip is not None else None

    def get_participants(self, only_active=True):
        """ Renvoyer les destinataires du message """
        return self.thread.get_participants(only_active=only_active)

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

    # Setter
    def remove(self):
        """ Supprimer le message """
        self.delete()
        self.thread.delete() if self.thread.counter == 0 else self.thread.save(force_update=True)

    # Privé
    def _get_similar_messages(self, messages, ratio=0.8):
        """ Renvoyer le nombre de messages similaires dans un queryset de messages """
        return len([True for message in messages if self.get_similarity(message) >= ratio])

    # Propriétés
    geoip = property(get_geoip)
    html = property(get_text_html)
    ip_address = property(IPPointModel.get_ip_address, IPPointModel.set_ip)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer le message dans la base de données """
        self.text = self.text.strip()
        if self.name == '' and self.author is not None:
            self.name = self.author.username
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
            return True
        return False

    def __str__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return """Post #{thread:010} "{message}" """.format(thread=self.thread_id, message=truncate_ellipsis(self.text, 24))

    def get_absolute_url(self):
        """ Renvoyer l'URL de l'objet """
        return self.thread.get_absolute_url()

    # Métadonnées
    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        permissions = (("can_force_send", "Can force send messages"),)
        app_label = 'forum'
