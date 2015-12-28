# coding: utf-8
from django import template

register = template.Library()


@register.filter(name="is_ignoring")
def is_ignoring(ignorer, user):
    """ Renvoyer si un utilisateur en ignore un autre """
    return ignorer.forum_ignorelist.is_ignored(user)
