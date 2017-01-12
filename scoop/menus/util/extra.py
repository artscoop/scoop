# coding: utf-8
from django.urls.base import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from scoop.messaging.models.recipient import Recipient

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


class Mails(Item):
    """ Menu Inbox (messaging) """

    # Configuration
    label = _("Inbox")
    target = reverse_lazy('messaging:inbox')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()

    def get_label(self, request=None):
        output = "{label} <span class='label primary'>{unread}</span>".format(label=self.label, unread=Recipient.objects.get_unread_count(request.user))
        return mark_safe(output)


class UserSearch(Item):
    """ Rechercher des utilisateurs """

    # Configuration
    label = _("Search")
    target = reverse_lazy('user:profile-search')

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()
