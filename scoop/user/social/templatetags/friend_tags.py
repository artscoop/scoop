# coding: utf-8
from django import template

register = template.Library()


@register.filter
def mutual_friend_count(user, target):
    """ Renvoyer le nombre d'amis en commun avec un utilisateur """
    return user.friends.get_mutual_users(target, count=True)


@register.assignment_tag
def mutual_friends(user, target):
    """ Renvoyer les amis en commun avec un utilisateur  """
    return user.friends.get_mutual_users(target, count=False)


@register.filter
def is_friend(user, target):
    """ Renvoyer si un utilisateur est ami avec un autre """
    return user.friends.is_friend(target)


@register.filter
def is_friend_waiting(user, target):
    """ Renvoyer si une demande d'ami à target existe encore """
    return user.friends.is_pending(target)
