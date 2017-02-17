# coding: utf-8
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from scoop.user.social.models.friend.friendgroup import FriendGroup
from scoop.user.social.models.friend.friendlist import FriendList


@admin.register(FriendList)
class FriendListAdmin(AjaxSelectAdmin):
    """ Admin des listes d'amis """
    list_select_related = True
    list_display = ['pk', 'get_friend_ids']
    list_filter = []
    list_editable = []
    readonly_fields = []
    fields = []


@admin.register(FriendGroup)
class FriendGroupAdmin(admin.ModelAdmin):
    """ Admin des groupes d'amis """
    list_select_related = True
    list_display = ['id', 'user', 'name', 'get_friend_count', 'get_data_repr']
    list_filter = []
    list_editable = []
    readonly_fields = ['user']
