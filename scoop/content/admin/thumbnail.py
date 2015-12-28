# coding: utf-8
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.models import Thumbnail
from scoop.core.util.django.admin import ViewOnlyModelAdmin
from scoop.core.util.shortcuts import addattr


class ThumbnailAdmin(ViewOnlyModelAdmin):
    """ Administration des références miniatures easy-thumbnail """
    list_select_related = True
    list_display = ['id', 'name', 'get_thumbnail', 'source', 'storage_hash', 'modified']
    list_display_links = ['id']
    list_filter = []
    actions = []

    @addattr(allow_tags=True, short_description=_("Picture"))
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
admin.site.register(Thumbnail, ThumbnailAdmin)
