# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr
from scoop.forum.forms.forum import ForumAdminForm
from scoop.forum.models.forum import Forum


class ForumAdmin(AjaxSelectAdmin, admin.ModelAdmin):
    """ Administration de forum """
    list_display = ['id', 'get_thumbnail', 'name', 'description', 'root', 'get_parents', 'get_topic_count_admin', 'locked', 'access_level']
    list_display_links = ['id']
    list_editable = ['root', 'name']
    list_filter = ['locked', 'visible', 'root', 'access_level']
    list_select_related = True
    list_per_page = 50
    search_fields = ['name', 'description']
    readonly_fields = ['topic_count']
    actions_on_bottom = True
    actions = ['update_count']
    save_on_top = True
    filter_horizontal = ['topics', 'forums', 'moderators']
    inlines = []
    form = make_ajax_form(Forum, {'moderators': 'user'}, ForumAdminForm)
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    fieldsets = ((_("Forum"), {'fields': ('name', 'description', 'access_level', 'visible', 'locked')}), (_("Settings"), {'fields': ('forums', 'root', 'icon', 'weight')}))

    # Actions
    @addattr(short_description=_("Update topic count"))
    def update_count(self, request, queryset):
        """ Recalculer le nombre de sujets des forums """
        for forum in queryset:
            forum.get_topic_count()
        self.message_user(request, _("Forum topic counts have been updated."))

    # Getter
    @addattr(allow_tags=True, short_description=_("Picture"))
    def get_thumbnail(self, obj):
        """ Renvoyer une miniature de l'icône """
        return obj.get_icon_thumbnail_html(size=(48, 24))

    @addattr(allow_tags=True, short_description=_("Found in"))
    def get_parents(self, obj):
        """ Renvoyer les parents du forum """
        return "<br>".join([str(item) for item in obj.get_parents()]) or None

    # Overrides
    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut """
        qs = super(ForumAdmin, self).queryset(request)
        return qs


class IgnoreAdmin(admin.ModelAdmin):
    """ Administration des ignore """
    list_select_related = True
    list_display = ['id', 'blocker', 'blockee', 'type']
    list_editable = []
    list_filter = ['type']
    search_fields = []

# Enregistrer les classes d'administration
admin.site.register(Forum, ForumAdmin)
