# coding: utf-8
from django import template

register = template.Library()


@register.filter(name="has_muted")
def has_muted(ignorer, user):
    """ Renvoyer si un utilisateur en ignore un autre """
    return ignorer.forum_mutelist.is_muted(user)


@register.filter(name='message_html')
def message_html(message, request):
    """
    Renvoyer le HTML du message 
    :param message: 
    :type message: scoop.forum.models.Message
    :param request: 
    :return: 
    """
    return message.get_text_html(request)


@register.filter(name='threads')
def label_threads(label, request):
    """
    Renvoyer les fils pour le label
    
    :param label: Étiquette
    :param request: requête
    :type label: scoop.forum.models.Label
    :type request: django.http.HttpRequest
    :return: un queryset de Thread
    """
    return label.get_threads(request)
