# coding: utf-8
import logging
from functools import wraps

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import ContentType
from django.http.response import Http404
from django.utils.translation import ugettext_lazy as _
from scoop.user.models.profile import BaseProfile

_LOGGER = logging.getLogger(__name__)


def is_authenticated(user):
    """ Renvoyer si l'utilisateur est un membre enregistré """
    return user.is_authenticated()


def is_staff(user):
    """ Renvoyer si l'utilisateur fait partie du personnel autorisé """
    return user.is_staff or user.is_superuser


def is_superuser(user):
    """ Renvoyer si l'utilisateur est un super utilisateur """
    return user.is_superuser


def is_anonymous(user):
    """ Renvoyer si l'utilisateur est un visiteur anonyme  """
    return user.is_anonymous()


def is_male(user):
    """ Renvoyer si l'utilisateur est un homme """
    return is_authenticated(user) and user.profile.gender == BaseProfile.MALE


def is_female(user):
    """ Renvoyer si l'utilisateur est une femme """
    return is_authenticated(user) and user.profile.gender == BaseProfile.FEMALE


def is_queer(user):
    """ Renvoyer si l'utilisateur n'a pas un genre de base """
    return is_authenticated(user) and user.profile.gender == BaseProfile.GENDER_OTHER


def staff_or_404(view_func):
    """ Décorateur qui renvoie un 404 si l'utilisateur n'est pas du personnel """

    def _checklogin(request, *args, **kwargs):
        if request.user.is_active and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        else:
            raise Http404

    return wraps(view_func)(_checklogin)


def check_permission(user, mode_name, app_label, model_name):
    """
    Renvoie si un utilisateur a une permission précise
    :param mode_name: généralement add, change ou delete
    :param app_label: étiquette de l'application
    :param model_name: nom du modèle dans les ContentTypes
    """
    p = '{}.{}_{}}'.format(app_label, mode_name, model_name)
    return user.is_active and user.has_perm(p)


def can_edit_or_404(request, user):
    """
    Renvoyer si l'utilisateur connecté a des droits en écriture
    sur un autre, sinon lever une exception 404
    """
    if not request.user.can_edit(user):
        raise Http404(_("You have no permission over this user."))


def register_custom_permissions(permissions, app_label):
    """
    Créer une ou plusieurs nouvelles permissions
    :param permissions: tuple de tuples contenant le nom et l'étiquette de la permission
    :param app_label: étiquette de l'application
    """
    ct, _ = ContentType.objects.get_or_create(model='', app_label=app_label, defaults={'name': app_label})
    for codename, name in permissions:
        _, _ = Permission.objects.get_or_create(codename=codename, content_type__pk=ct.id, defaults={'name': name, 'content_type': ct})


def get_profile_model():
    """ Renvoyer le modèle utilisé comme profil utilisateur """
    model = None
    profile_string = getattr(settings, 'AUTH_PROFILE_MODULE', None)
    if profile_string:
        app_label, model_label = profile_string.split('.')
        model = apps.get_model(app_label, model_label)
    return model
