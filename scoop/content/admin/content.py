# coding: utf-8
from __future__ import absolute_import

import datetime

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.template.defaultfilters import date as datefilter
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scoop.content.admin.inline import CategoryTranslationInlineAdmin, PictureInlineAdmin
from scoop.content.forms.content import ContentAdminForm
from scoop.content.models.content import Category, Content
from scoop.content.models.picture import Picture
from scoop.content.util.admin import PicturedModelAdmin
from scoop.core.templatetags.html_tags import list_enumerate
from scoop.core.util.model.widgets import AdminSplitDateTime
from scoop.core.util.shortcuts import addattr

__all__ = ['ContentAdminModelAdmin', 'CategoryAdmin']


class ContentAdminModelAdmin(AjaxSelectAdmin, PicturedModelAdmin):
    """ Administration des contenus """

    list_display = ['id', 'get_uuid_html', 'title', 'get_authors', 'get_created', 'is_published', 'featured', 'sticky', 'get_comment_count_admin', 'category', 'access', 'get_image', 'has_picture', 'get_picture_set']
    list_filter = ['published', 'category', 'featured', 'sticky', 'pictured']
    list_display_links = ['id', 'title']
    list_per_page = 25
    readonly_fields = ['slug']
    list_select_related = True
    save_on_top = False
    search_fields = ['title', 'slug', 'published', 'body']
    ordering = ['-id']
    inlines = [PictureInlineAdmin]
    filter_horizontal = ['tags', 'authors']
    form = make_ajax_form(Content, {'authors': 'user', 'picture': 'picture', 'parent': 'content'}, ContentAdminForm)
    fieldsets = ((_("Content"), {'fields': ('title', 'body', 'format', 'authors', 'category', 'access', 'published', 'sticky', 'commentable', 'picture')}),
                 (_("Plus"), {'fields': ('slug', 'parent', 'locked', 'featured', 'teaser', 'created', 'publish', 'expire', 'tags')}))
    actions = ['publish', 'unpublish', 'stick', 'unstick']
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    ignore_duplicate_revisions = True

    # Actions
    @addattr(short_description=_("Unpublish selected content"))
    def unpublish(self, request, queryset):
        """ Dépublier un queryset de contenus """
        for content in queryset:
            content.publish_plain(value=False)
        self.message_user(request, _("Selected content has been unpublished."))

    @addattr(short_description=_("Publish selected content"))
    def publish(self, request, queryset):
        """ Publier un queryset de contenus """
        for content in queryset:
            content.publish_plain(True)
        self.message_user(request, _("Selected content has been published."))

    @addattr(short_description=_("Spread publication of content, one a day."))
    def spread_publish(self, request, queryset):
        """ Étaler la publication des articles à un par jour """
        day = timezone.now() + datetime.timedelta(days=1)
        count = len(queryset)
        for content in queryset:
            if not content.is_published():
                content.set_publish_dates(day, None)
                day += datetime.timedelta(days=1)
        self.message_user(request, _("{count} contents have been scheduled for interval publication.").format(count=count))

    @addattr(short_description=_("Pin selected content"))
    def stick(self, request, queryset):
        """ Définir les contenus comme épinglés """
        queryset.update(sticky=True)
        self.message_user(request, _("Selected content has been pinned."))

    @addattr(short_description=_("Unpin selected content"))
    def unstick(self, request, queryset):
        """ Définir les contenus comme non épinglés """
        queryset.update(sticky=False)
        self.message_user(request, _("Selected content has been unpinned."))

    # Getter
    @addattr(allow_tags=True, short_description=_("Picture"))
    def get_image(self, obj):
        """ Renvoyer le tag de l'image par défaut du contenu """
        if obj.picture is not None:
            return "{}".format(obj.picture.get_thumbnail_html(size=(48, 20)))

    @addattr(admin_order_field='created', short_description=_("Created"))
    def get_created(self, obj):
        """ Renvoyer la date de création du contenu """
        return datefilter(obj.created, "j M Y G:i")

    @addattr(short_description=_("Authors"))
    def get_authors(self, obj):
        """ Renvoyer la liste des auteurs du contenu """
        return list_enumerate(obj.authors.all()) or _("None")

    # Overrides
    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut """
        return Content.objects if request else Content.objects

    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Renvoyer le champ de formulaire pour un champ db """
        if db_field.name == 'created':
            kwargs['widget'] = AdminSplitDateTime()
        return super(ContentAdminModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """ Renvoyer le formulaire """
        self.current_content = obj
        form = super(ContentAdminModelAdmin, self).get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['picture'].queryset = Picture.objects.filter(author=request.user)
        return form

    def get_object(self, request, object_id, from_field=None):
        """ Renvoyer un objet """
        obj = super(ContentAdminModelAdmin, self).get_object(request, object_id)
        if obj is not None and not obj.authors.exists():
            obj.authors = [request.user]  # Par défaut l'utilisateur en cours est l'auteur
        return obj

    def save_model(self, request, obj, form, change):
        """ Enregistrer un objet """
        obj.save()
        if obj.authors.count() == 0:
            obj.authors.add(request.user)  # Par défaut ajouter l'utilisateur en cours aux auteurs

    def save_formset(self, request, form, formset, change):
        """ Enregistrer les instances d'un formulaire groupé """
        if formset.model == Content:
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.authors.all().count() == 0:
                    instance.authors.add(request.user)
                    instance.save()
        else:
            formset.save()
        super(ContentAdminModelAdmin, self).save_formset(request, form, formset, change)


class CategoryAdmin(admin.ModelAdmin):
    """ Administration des types de contenus """
    list_select_related = True
    list_display = ['id', 'get_name', 'get_plural', 'url', 'get_description']
    list_editable = ['url']
    search_fields = []
    readonly_fields = ['data']
    inlines = [CategoryTranslationInlineAdmin]
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'

# Enregistrer les classes d'administration
admin.site.register(Content, ContentAdminModelAdmin)
admin.site.register(Category, CategoryAdmin)
