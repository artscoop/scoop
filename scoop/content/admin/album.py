# coding: utf-8
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from genericadmin.admin import GenericAdminModelAdmin

from scoop.content.admin.inline import AlbumPictureInlineAdmin
from scoop.content.forms.album import AlbumAdminForm
from scoop.content.models.album import Album
from scoop.content.util.admin import PicturedModelAdmin
from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin
from scoop.core.util.django.admin import GenericModelUtil


@admin.register(Album)
class AlbumAdmin(AjaxSelectAdmin, PicturedModelAdmin, GenericAdminModelAdmin, AutoAuthoredModelAdmin, GenericModelUtil):
    """ Administration des albums d'images """

    # Configuration
    list_select_related = True
    list_display = ['id', 'author', 'name', 'description', 'parent', 'get_picture_count', 'get_picture_set']
    list_display_links = ['id']
    list_filter = []
    actions = []
    form = make_ajax_form(Album, {'author': 'user', 'pictures': 'picture'}, AlbumAdminForm)
    fieldsets = ((_("Album"), {'fields': ('author', 'name', 'description', 'content_type', 'object_id', 'parent')}),)
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    inlines = [AlbumPictureInlineAdmin]
