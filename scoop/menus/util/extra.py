# coding: utf-8
from django.urls.base import reverse
from django.utils.translation import ugettext_lazy as _

from scoop.menus.elements.item import Item


class Login(Item):
    """ Menu connexion """

    # Configuration
    label = _("Login")
    target = reverse('user:login')

    # Overrides
    def is_visible(self, request):
        return request.user.is_anonymous()


class Logout(Item):
    """ Menu connexion """

    # Configuration
    label = _("Logout")
    target = reverse('user:logout')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()


class Admin(Item):
    """ Menu admin """

    # Configuration
    label = _("Manage")
    target = reverse('admin:index')

    # Overrides
    def is_visible(self, request):
        return request.user.is_superuser
