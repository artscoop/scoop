# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.models import Thumbnail

from scoop.content.models.advertisement import Advertisement
from scoop.content.models.album import Album
from scoop.content.models.attachment import Attachment
from scoop.content.util.admin import PicturedModelAdmin
from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin
from scoop.core.util.django.admin import GenericModelUtil, ViewOnlyModelAdmin
from scoop.core.util.shortcuts import addattr


class TagAdmin(admin.ModelAdmin):
    """ Administration des étiquettes de contenu """
    list_select_related = True
    list_display = ['id', 'name', 'icon']
    list_editable = []
    list_filter = []
    search_fields = []


class AdvertisementAdmin(AutoAuthoredModelAdmin):
    """ Administration des annonces publicitaires """
    list_select_related = True
    list_display = ['id', 'name', 'group', 'network', 'weight', 'width', 'height', 'get_datetime_format', 'views']
    list_editable = []
    list_filter = ['group', 'network']
    search_fields = ['group', 'name']
    readonly_fields = []
    order_by = ['group']


class AlbumAdminModelAdmin(AjaxSelectAdmin, PicturedModelAdmin, admin.ModelAdmin):
    """ Administration des albums d'images """
    list_select_related = True
    list_display = ['id', 'author', 'name', 'description', 'parent', 'get_picture_count', 'get_picture_set']
    list_display_links = ['id']
    list_filter = []
    actions = []
    form = make_ajax_form(Album, {'author': 'user', 'pictures': 'picture'})
    fieldsets = ((_(u"Album"), {'fields': ('author', 'name', 'description', ('content_type', 'object_id'), 'parent', 'pictures')}),)


class AttachmentAdmin(admin.ModelAdmin, GenericModelUtil):
    """ Administration des fichiers de pièces jointes """
    list_select_related = True
    list_display = ['id', 'author', 'file', 'name', 'mimetype', 'get_content_type_info', 'get_content_object_info', 'exists']
    list_filter = ['content_type', 'mimetype']
    search_fields = ['file', 'author__username', 'mimetype']
    readonly_fields = []
    form = make_ajax_form(Album, {'author': 'user'})


class ThumbnailAdmin(ViewOnlyModelAdmin):
    """ Administration des références miniatures easy-thumbnail """
    list_select_related = True
    list_display = ['id', 'name', 'get_thumbnail', 'source', 'storage_hash', 'modified']
    list_display_links = ['id']
    list_filter = []
    actions = []

    @addattr(allow_tags=True, short_description=_(u"Picture"))
    def get_thumbnail(self, obj):
        """ Retourner le contenu de la miniature """
        return "<img src='%(media)s%(url)s' title='%(url)s' style='height:24px;'>" % {'url': obj.name, 'media': settings.MEDIA_URL}


class SourceAdmin(ViewOnlyModelAdmin):
    """ Administration des sources de miniatures easy-thumbnails """
    list_select_related = True
    list_display = ['id', 'name', 'storage_hash', 'modified']
    list_display_links = ['id']
    list_filter = []
    actions = []

# Enregistrer les classes d'administration
admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Thumbnail, ThumbnailAdmin)
admin.site.register(Album, AlbumAdminModelAdmin)
admin.site.register(Attachment, AttachmentAdmin)
