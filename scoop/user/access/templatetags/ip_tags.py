# coding: utf-8
from django import template
from scoop.user.access.models.ip import IP
from scoop.user.access.models.userip import UserIP

register = template.Library()


@register.assignment_tag(name='to_ip')
def get_ip_from_string(ip_string):
    """ Assigner un objet IP depuis une chaîne au format A.B.C.D """
    return IP.objects.get_by_ip(ip_string)


@register.filter(name='ips')
def user_ips(user):
    """ Renvoyer les IP d'un utilisateur """
    return UserIP.objects.for_user(user)
