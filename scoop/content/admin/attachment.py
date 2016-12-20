# coding: utf-8
from ajax_select import make_ajax_form
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.content.models.album import Album
from scoop.content.models.attachment import Attachment
from scoop.core.util.django.admin import GenericModelUtil
from scoop.core.util.shortcuts import addattr


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin, GenericModelUtil):
    """ Administration des fichiers de pièces jointes """

    # Configuration
    list_select_related = True
    list_display = ['id', 'author', 'file', 'name', 'get_file_size', 'get_content_type_info', 'get_content_object_info', 'exists']
    list_filter = ['content_type', 'mimetype', 'acl_mode']
    search_fields = ['file', 'author__username', 'mimetype']
    readonly_fields = []
    form = make_ajax_form(Album, {'author': 'user'})
    actions = ['detach']

    # Actions
    @addattr(short_description=_("Detach selected attachments"))
    def detach(self, request, queryset):
        """ Disjoindre le fichier de sa cible """
        count = 0
        for item in queryset:
            count += 1 if item.detach() else 0
        self.message_user(request, _("{count} attachments have been detached.").format(count=count))
