# coding: utf-8
from django import template
from scoop.messaging.models import Message, Recipient, Thread
from scoop.messaging.models.alert import Alert
from scoop.messaging.util.text import format_message

register = template.Library()


@register.filter(name="format")
def message_format(text):
    """ Renvoyer un texte HTML reformaté """
    return format_message(text, strip_tags=True)


@register.filter(name="is_unread")
def is_unread(thread, user):
    """ Renvoyer si un fil est non lu pour un utilisateur """
    if hasattr(thread, 'is_unread'):
        return thread.is_unread(user)


@register.filter(name="received_messages")
def get_received_messages(user):
    """
    Renvoyer la liste de tous les messages à destination de l'utilisateur
    - Les messages pris en compte sont ceux des sujets où user participe
    - Les messages ne sont pas envoyés par user
    """
    if getattr(user, 'is_authenticated', lambda: False)():
        messages = Message.objects.for_user(user)
        return messages


@register.filter(name="received_messages_count")
def get_received_messages_count(user):
    """ Renvoyer le nombre de messages à destination de l'utilisateur """
    if getattr(user, 'is_authenticated', lambda: False)():
        return get_received_messages(user).count()


@register.filter(name="unread_messages")
def get_unread_count(user):
    """ Renvoyer le nombre de messages non lus par un utilisateur """
    if getattr(user, 'is_authenticated', lambda: False)():
        unread = Recipient.objects.get_unread_count(user)
        return unread


@register.filter(name="unread_alerts")
def get_unread_alert_count(user):
    """ Renvoyer le nombre d'alertes non lues par un utilisateur """
    if getattr(user, 'is_authenticated', lambda: False)():
        unread = Alert.objects.get_unread_count(user)
        return unread


@register.assignment_tag(name="interlocutors")
def get_interlocutors(user, thread):
    """ Récupérer les interlocuteurs de l'utilisateur, dans un thread ou dans tous les threads """
    if thread is not None and not user.is_anonymous():
        return thread.get_users(exclude=user)
    return Recipient.objects.related_users(user)


@register.filter(name="recipients")
def get_recipients(thread, user=None):
    """ Renvoyer tous les destinataires d'un fil excepté un utilisateur """
    if thread is not None:
        if user is not None:
            return thread.get_users(exclude=user)
        return thread.get_users()
