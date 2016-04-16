# coding: utf-8
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from scoop.user.models.user import User


class CaseInsensitiveEmailModelBackend(ModelBackend):
    """ Backend d'authentification via identifiants email/username """

    def authenticate(self, username=None, password=None, **kwargs):
        """ Authentifier un utilisateur via identifiants """
        try:
            user = User.objects.active().get(Q(username__iexact=username.strip()) | Q(email__iexact=username.strip()))
            if user.check_password(password) and user.can_login():
                return user
            else:
                return None
        except User.DoesNotExist:
            return None
