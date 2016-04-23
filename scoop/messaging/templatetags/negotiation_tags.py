# coding: utf-8
from django import template
from scoop.messaging.models.negotiation import Negotiation

register = template.Library()


@register.filter(name="has_negotiation")
def has_negotiation(user, target):
    """ Renvoyer si l'utilisateur a négocié avec la cible """
    return Negotiation.objects.has_negotiation(user, target)
