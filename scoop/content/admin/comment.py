# coding: utf-8
from __future__ import absolute_import

from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE

from scoop.content.admin.inline import PictureInlineAdmin
from scoop.content.forms.comment import CommentAdminForm, CommentForm
from scoop.content.models.comment import Comment
from scoop.core.util.django.admin import GenericModelUtil
from scoop.core.util.shortcuts import addattr

__all__ = ['CommentAdmin']


class CommentInlineAdmin(GenericTabularInline):
    """ Inline admin des commentaires """
    model = Comment
    form = CommentForm
    formfield_overrides = {models.TextField: {'widget': TextInput}}


class CommentAdmin(AjaxSelectAdmin, admin.ModelAdmin, GenericModelUtil):
    """ Administration des commentaires """

    list_display = ['id', 'author', 'name', 'body', 'moderated', 'get_content_type_info', 'get_content_object_info', 'ip']
    list_filter = ['visible', 'spam', 'moderated']
    readonly_fields = ['author']
    list_select_related = True
    search_fields = ['body', 'url', 'email', 'name']
    ordering = ['-id']
    inlines = [PictureInlineAdmin]
    form = CommentAdminForm
    actions = ['set_spam']
    save_on_top = True
    fieldsets = ((_("Comment"), {'fields': ('body', ('content_type', 'object_id',), 'visible', 'email', 'url', 'name',)}),)
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'

    @addattr(short_description=_("Mark selected comments as spam."))
    def set_spam(self, request, queryset):
        """ Marquer un queryset de commentaires comme spam """
        for comment in queryset:
            comment.set_spam(True)
        self.message_user(request, _("Selected comments have been marked as spam."))

    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Renvoyer le champ de formulaire pour un champ db """
        if db_field.name == 'body':
            kwargs['widget'] = TinyMCE()
        return super(CommentAdmin, self).formfield_for_dbfield(db_field, **kwargs)

# Enregistrer les classes d'administration
admin.site.register(Comment, CommentAdmin)
