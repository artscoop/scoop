# coding: utf-8
from ajax_select import make_ajax_form
from django.contrib import admin
from scoop.content.models.advertisement import Advertisement
from scoop.content.models.album import Album
from scoop.content.models.attachment import Attachment
from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin
from scoop.core.util.django.admin import GenericModelUtil


class TagAdmin(admin.ModelAdmin):
    """ Administration des étiquettes de contenu """
    list_select_related = True
    list_display = ['id', 'name', 'icon']
    list_editable = []
    list_filter = []
    search_fields = []


@admin.register(Advertisement)
class AdvertisementAdmin(AutoAuthoredModelAdmin):
    """ Administration des annonces publicitaires """
    list_select_related = True
    list_display = ['id', 'name', 'group', 'network', 'weight', 'width', 'height', 'get_datetime_format', 'views']
    list_editable = []
    list_filter = ['group', 'network']
    search_fields = ['group', 'name']
    readonly_fields = []
    order_by = ['group']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin, GenericModelUtil):
    """ Administration des fichiers de pièces jointes """
    list_select_related = True
    list_display = ['id', 'author', 'file', 'name', 'mimetype', 'get_content_type_info', 'get_content_object_info', 'exists']
    list_filter = ['content_type', 'mimetype']
    search_fields = ['file', 'author__username', 'mimetype']
    readonly_fields = []
    form = make_ajax_form(Album, {'author': 'user'})
