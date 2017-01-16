# coding: utf-8
from django.urls.base import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from scoop.menus.elements.item import Item


class StaffAdmin(Item):
    """ Menu admin """

    # Configuration
    label = _("Manage")
    target = reverse_lazy('admin:index')

    # Overrides
    def is_visible(self, request):
        return request.user.is_superuser
