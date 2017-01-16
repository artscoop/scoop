# coding: utf-8
from django.urls.base import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from scoop.messaging.models.recipient import Recipient

from scoop.menus.elements.item import Item


class UserLogin(Item):
    """ Menu connexion """

    # Configuration
    label = _("Login")
    target = reverse_lazy('user:login')

    # Overrides
    def is_visible(self, request):
        return request.user.is_anonymous()


class UserLogout(Item):
    """ Menu connexion """

    # Configuration
    label = _("Logout")
    target = reverse_lazy('user:logout')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()


class UserSelf(Item):
    """ Afficher son propre profil """

    # Configuration
    label = _("My profile")
    target = reverse_lazy('user:self-view')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()


class UserEditSelf(Item):
    """ Modifier son propre profil """

    # Configuration
    label = _("Edit my profile")
    target = reverse_lazy('user:self-edit')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()


class UserSearch(Item):
    """ Rechercher des utilisateurs """

    # Configuration
    label = _("Search")
    target = reverse_lazy('user:profile-search')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()
