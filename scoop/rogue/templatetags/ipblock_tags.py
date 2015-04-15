# coding: utf-8
from __future__ import absolute_import

from django.template import Library

from scoop.rogue.models.ipblock import IPBlock

register = Library()


@register.filter
def has_ip_blocked(user):
    """ Renvoyer si un utilisateur est bloqué par IP """
    return IPBlock.objects.is_user_blocked(user)


@register.filter
def get_blocked_ips(user):
    """ Renvoyer les IP bloquées de l'utilisateur """
    return IPBlock.objects.user_blocked_ips(user, True)


@register.filter
def get_unblocked_ips(user):
    """ Renvoyer les IP non bloquées de l'utilisateur """
    return IPBlock.objects.user_blocked_ips(user, False)
