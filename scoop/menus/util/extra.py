# coding: utf-8
from django.urls.base import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from scoop.menus.elements.item import Item


class Login(Item):
    """ Menu connexion """

    # Configuration
    label = _("Login")
    target = reverse_lazy('user:login')

    # Overrides
    def is_visible(self, request):
        return request.user.is_anonymous()


class Logout(Item):
    """ Menu connexion """

    # Configuration
    label = _("Logout")
    target = reverse_lazy('user:logout')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()


class Admin(Item):
    """ Menu admin """

    # Configuration
    label = _("Manage")
    target = reverse_lazy('admin:index')

    # Overrides
    def is_visible(self, request):
        return request.user.is_superuser
