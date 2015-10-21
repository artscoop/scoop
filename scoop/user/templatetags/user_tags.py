# coding: utf-8
from __future__ import absolute_import

from django import template
from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.core.util.data.numbers import round_left
from scoop.user.models import User, Visit
from scoop.user.models.profile import BaseProfile
from scoop.user.util.auth import check_permission

register = template.Library()


@register.filter
def picture(user, request=None):
    """ Renvoyer l'image de profil utilisateur si accessible à l'utilisateur courant """
    if hasattr(user, 'profile'):
        return user.profile.get_picture(request)
    elif isinstance(user, BaseProfile):
        return user.get_picture(request)
    return None


@register.filter
def picture_url(user, request=None):
    """ Renvoyer l'URL de l'image de profil utilisateur """
    relative_path = picture(user, request=request)
    return "{}{}".format(settings.MEDIA_URL, relative_path)


# Permissions
@register.filter
def can_edit(user, target):
    """ Renvoyer si l'utilisateur peut en modifier un autre """
    if user and target:
        return user.is_authenticated() and user.can_edit(target)


@register.filter
def can_see(user, target):
    """ Renvoyer si l'utilisateur peut en voir un autre """
    if user and target:
        return user.can_see(target)


@register.filter
def has_add_perm(user, target):
    """ Renvoyer si l'utilisateur a le droit d'ajouter un objet du même type que la cible """
    content_type = ContentType.objects.get_for_model(target)
    return check_permission(user, 'add', content_type.app_label, content_type.name)


# État en ligne des utilisateurs
@register.assignment_tag
def online_users(*args, **kwargs):
    """ Renvoyer les utilisateurs en ligne """
    return User.get_online_users()


@register.assignment_tag(name="online_count")
def online_count():
    """ Assigner à une variable le nombre d'utilisateurs en ligne """
    return User.get_online_count()


@register.simple_tag
def show_online_count(name="show_online_count"):
    """ Afficher le nombre d'utilisateurs en ligne """
    return User.get_online_count()


@register.inclusion_tag('user/display/user/templatetag/online-status.html', name='online_status')
def online_status(user, mode="text"):
    """ Afficher le statut en ligne d'un utilisateur """
    return {'user': user, 'mode': mode}


# Visites
@register.assignment_tag(name="visitors_to")
def visitors_to(user, count=8, *args, **kwargs):
    """
    Assigner à une variable les visiteurs du profil d'un utilisateur
    :param count: nombre d'utilisateurs maximum à renvoyer
    :returns: un queryset d'utilisateurs possédant un attribut "when"
     qui correspond au timestamp de sa visite au profil
    """
    if user.is_authenticated():
        return Visit.objects.to_user(user, as_users=True)[0:count]
    return Visit.objects.none()


@register.assignment_tag(name="visited_by")
def visited_by(user, count=8, *args, **kwargs):
    """
    Assigner à une variable les profils visités par un utilisateur
    :param count: nombre d'utilisateurs maximum à renvoyer
    :returns: un queryset d'utilisateurs possédant un attribut "when"
     qui correspond au timestamp de sa visite au profil
    """
    if user.is_authenticated():
        return Visit.objects.by_user(user, as_users=True)[0:count]
    return Visit.objects.none()


@register.filter(name='has_been_visited')
def has_visitors(user):
    """ Renvoyer si un utilisateur a déjà eu des visites """
    return Visit.objects.has_visitors(user) if user.is_authenticated() else False


@register.filter(name='has_made_visits')
def made_visits(user):
    """ Renvoyer si un utilisateur a déjà visité des profils """
    return Visit.objects.has_made_visits(user)


@register.simple_tag(name='user_distance')
def show_distance(user1, user2, unit=None, digits=2):
    """
    Afficher la distance entre deux villes de profils
    Ne rien afficher si les deux profils sont dans la même ville
    :param unit: unité de distance, entre km|m|mi|yd|ft|nmi
    :param digits: limiter le résultat aux n chiffres les plus significatifs
    """
    if not any([u.is_anonymous() or not u.profile.city for u in [user1, user2]]):
        distance = CoordinatesModel.convert_km_to(user1.profile.city.get_distance(user2.profile.city), unit or 'km')
        if distance > 0:
            unit = unit if unit in CoordinatesModel.UNIT_RATIO else 'km'
            return "{}{}".format(intcomma(round_left(distance, digits)), unit or 'km')
    return ""


@register.simple_tag(name='user_cardinal')
def show_cardinal(user1, user2, mode=None):
    """
    Afficher le cardinal de direction entre deux villes de profils
    Ne rien afficher si les deux profils sont dans la même ville
    """
    if not any([u.is_anonymous() or not u.profile.city for u in [user1, user2]]):
        return user1.profile.city.get_cardinal_position(user2.profile.city)
    return ""


@register.filter(name='distance')
def distance_to(user1, user2):
    """ Renvoyer la distance en km entre deux villes de profils """
    if not any([u.is_anonymous() or not u.profile.city for u in [user1, user2]]):
        distance = user1.profile.city.get_distance(user2.profile.city)
        return distance
    return ""


@register.filter(name='by_auth')
def string_by_auth(user, value):
    """
    Renvoyer une chaîne si l'utilisateur est authentifié, sinon une autre
    :param value: chaîne contenant deux valeurs séparées par des virgules,
        la première valeur étant renvoyée si l'utilisateur est authentifié
    :type value: str or list or tuple
    """
    if isinstance(value, str):
        strings = value.split(',')
    elif isinstance(value, (list, tuple)):
        strings = [str(item) for item in value]
    else:
        strings = [_("yes"), _("no")]
    return strings[0] if user.is_authenticated() else strings[1]


@register.filter(name='by_staff')
def string_by_staff(user, value):
    """
    Renvoyer une chaîne si l'utilisateur est du personnel, sinon une autre
    :param value: chaîne contenant deux valeurs séparées par des virgules,
        la première valeur étant renvoyée si l'utilisateur est du personnel
    :type value: str or list or tuple
    """
    if isinstance(value, str):
        strings = value.split(',')
    elif isinstance(value, (list, tuple)):
        strings = [str(item) for item in value]
    else:
        strings = [_("yes"), _("no")]
    return strings[0] if user.is_staff else strings[1]
