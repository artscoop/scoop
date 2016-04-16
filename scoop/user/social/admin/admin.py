# coding: utf-8
from django.contrib import admin

from scoop.core.admin.filters import TimestampFilter
from scoop.core.util.django.admin import GenericModelUtil
from scoop.user.social.models.group import Group
from scoop.user.social.models.post import Post
from scoop.user.social.models.rating.like import Like


class GroupAdmin(admin.ModelAdmin):
    """ Admin des groupes sociaux """
    list_select_related = True
    list_display = ['slug', 'name', 'description', 'author']
    list_filter = [TimestampFilter]
    list_editable = []
    search_fields = []
    readonly_fields = ['author', 'time', 'slug']


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
admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
