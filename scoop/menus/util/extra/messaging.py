# coding: utf-8
from django.urls.base import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from scoop.menus.elements.item import Item
from scoop.messaging.models.recipient import Recipient


class MessagingInbox(Item):
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


class MessagingTrash(Item):
    """ Menu Inbox corbeille """

    # Configuration
    label = _("Trash")
    target = reverse_lazy('messaging:mailbox', kwargs={'mode': 'trash'})

    # Overrides
    def is_visible(self, request):
        return request.user.is_authenticated()
