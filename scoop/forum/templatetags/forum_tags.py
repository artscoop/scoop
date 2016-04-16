# coding: utf-8
from django import template


register = template.Library()


@register.filter(name="has_muted")
def has_muted(ignorer, user):
    """ Renvoyer si un utilisateur en ignore un autre """
    return ignorer.forum_mutelist.is_muted(user)
