# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.admin.filters import TimestampFilter
from scoop.core.util.django.admin import GenericModelUtil
from scoop.user.social.models.event import Event
from scoop.user.social.models.event.eventcategory import EventCategory
from scoop.user.social.models.friend.friendgroup import FriendGroup
from scoop.user.social.models.friend.friendlist import FriendList
from scoop.user.social.models.group import Group
from scoop.user.social.models.post import Post
from scoop.user.social.models.rating.like import Like


class FriendListAdmin(AjaxSelectAdmin):
    """ Admin des listes d'amis """
    list_select_related = True
    list_display = ['pk', 'get_friend_ids']
    list_filter = []
    list_editable = []
    readonly_fields = []
    fields = []


class FriendGroupAdmin(admin.ModelAdmin):
    """ Admin des groupes d'amis """
    list_select_related = True
    list_display = ['id', 'user', 'name', 'get_friend_count', 'get_data_repr']
    list_filter = []
    list_editable = []
    readonly_fields = ['user']


class GroupAdmin(admin.ModelAdmin):
    """ Admin des groupes sociaux """
    list_select_related = True
    list_display = ['slug', 'name', 'description', 'author']
    list_filter = [TimestampFilter]
    list_editable = []
    search_fields = []
    readonly_fields = ['author', 'time', 'slug']


class EventAdmin(AjaxSelectAdmin):
    """ Admin des événements """
    list_select_related = True
    list_display = ['author', 'title', 'description']
    list_filter = ['access']
    list_editable = []
    readonly_fields = ['author']


class EventCategoryInlineAdmin(admin.TabularInline):
    """ Admin inline des catégories d'événements """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = EventCategory
    max_num = len(settings.LANGUAGES)
    extra = 4
    formfield_overrides = {models.TextField: {'widget': admin.widgets.AdminTextInputWidget}}


class EventCategoryAdmin(admin.ModelAdmin):
    """ Admin des catégories d'événements """
    list_select_related = True
    list_display = ['icon', 'get_name', 'parent']
    list_filter = []
    list_editable = []
    search_fields = ['translations__name']
    readonly_fields = []
    inlines = [EventCategoryInlineAdmin, ]
    fieldsets = ((_("event category"), {'fields': ('icon', 'parent')}),)
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'


class PostAdmin(admin.ModelAdmin):
    """ Admin des posts de mur """
    list_select_related = True
    list_display = ['id', 'author', 'text', 'access', 'get_datetime_ago']
    list_filter = ['access']
    list_editable = []
    readonly_fields = []


class LikeAdmin(admin.ModelAdmin, GenericModelUtil):
    """ Admin des likes """
    list_select_related = True
    list_display = ['id', 'author', 'get_content_type_info', 'get_content_object_info']
    list_display_links = ['id']
    list_filter = ['content_type']
    actions = []
    save_on_top = True

# Enregistrer les classes d'administration
admin.site.register(FriendList, FriendListAdmin)
admin.site.register(FriendGroup, FriendGroupAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
