# coding: utf-8
from django.template import Library

register = Library()


@register.filter
def comment_is_editable(value, request):
    """ Renvoyer si un contenu peut être édité """
    try:
        return value.is_editable(request)
    except:
        return False
