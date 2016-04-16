# coding: utf-8
from django.contrib.auth.backends import ModelBackend

from scoop.user.models.user import User


class CaseInsensitiveModelBackend(ModelBackend):
    """ Backend d'authentification ignorant la casse """

    def authenticate(self, username=None, password=None):
        """ Authentifier un utilisateur via identifiants """
        try:
            user = User.objects.active().get(username__iexact=username.strip())
            if user.check_password(password) and user.can_login():
                return user
            else:
                return None
        except User.DoesNotExist:
            return None
        except Exception:
            return None
