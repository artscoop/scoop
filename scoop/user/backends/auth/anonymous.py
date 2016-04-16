# coding: utf-8
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

from scoop.user.models.user import User


def get_anon_user_name():
    """ Renvoyer le nom de l'utilisateur anonyme """
    return getattr(settings, "ANONYMOUS_USER_NAME", None)


@receiver(pre_save, sender=User)
def disable_anon_user_password_save(sender, **kwargs):
    """ Empêcher l'utilisation d'un mot de passe pour l'utilisateur anonyme """
    instance = kwargs['instance']
    if instance.username == get_anon_user_name() and instance.has_usable_password():
        raise ValueError("Can't set anonymous user password to something other than unusable password")


class AnonymousUserBackend(ModelBackend):
    """ Backend d'authentification pour l'utilisateur anonyme """

    def get_all_permissions(self, user_obj):
        """ Renvoyer les permissions de l'utilisateur """
        if user_obj.is_anonymous():
            if not hasattr(user_obj, '_perm_cache'):
                anon_user_name = get_anon_user_name()
                anon_user, _ = get_user_model().all_objects.get_or_create(pk=0, username=anon_user_name, is_active=False)
                anon_user.set_unusable_password()
                user_obj._perm_cache = self.get_all_permissions(anon_user)
            return user_obj._perm_cache
        return super(AnonymousUserBackend, self).get_all_permissions(user_obj)

    def authenticate(self, username=None, password=None):
        """ Authentifier via identifiants """
        if username == get_anon_user_name():
            return False
        return super(AnonymousUserBackend, self).authenticate(username, password)

    def has_perm(self, user_obj, perm, obj=None):
        """ Renvoyer si l'utilisateur possède une permission """
        if not user_obj.is_active and not user_obj.is_anonymous:
            return False
        return perm in self.get_all_permissions(user_obj)
