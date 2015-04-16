# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.apps.registry import apps
from django.contrib import admin, messages
from django.contrib.admin.options import StackedInline
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from scoop.content.admin.inline import PictureInlineAdmin
from scoop.core.abstract.user.authored import UseredModelAdmin
from scoop.core.util.data.dateutil import ages_dates, random_date
from scoop.core.util.model.model import shuffle_model
from scoop.core.util.shortcuts import addattr
from scoop.user.admin.filters import AgeFilter, ImageFilter, InitialFilter, OnlineFilter
from scoop.user.forms.profile import ProfileAdminForm, ProfileInlineAdminForm
from scoop.user.models.profile import BaseProfile
from scoop.user.util.auth import get_profile_model


class ProfileAdmin(AjaxSelectAdmin, UseredModelAdmin):
    """ Administration des profils """
    actions = ['deactivate', 'clear_picture', 'shuffle']
    actions_on_bottom = True
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    exclude = ()
    fieldsets = ((_(u"User"), {'fields': ('picture', 'gender', 'birth', 'city', 'doubt', 'banned',)}),)
    filter_horizontal = []
    form = make_ajax_form(get_profile_model(), {'city': 'citypm', 'picture': 'picture'}, ProfileAdminForm)
    formfield_overrides = {}
    inlines = [PictureInlineAdmin]
    list_display = ['get_id', 'get_user_link', 'get_image', 'gender', 'get_age', 'is_new', 'get_email', 'pictured', 'get_picture_set']
    list_editable = []
    list_filter = ['gender', 'user__date_joined', 'user__is_staff', OnlineFilter, AgeFilter, ImageFilter, InitialFilter]
    list_per_page = 25
    list_select_related = True
    ordering = ('-user',)
    radio_fields = {'gender': admin.VERTICAL}
    raw_id_fields = []
    related_search_fields = {'city': ('name', 'code', 'country__code2'), 'picture': ('title', 'description', 'keywords')}
    save_on_top = False
    search_fields = ['user__username', 'user__email']

    # Actions
    @addattr(short_description=_(u"Deactivate selected users"))
    def deactivate(self, request, queryset):
        """ Désactiver des utilisateurs """
        count = queryset.update(user__is_active=False)
        self.message_user(request, _(u"%(count)d users have been successfully deactivated.") % {"count": count}, messages.SUCCESS)

    @addattr(short_description=_(u"Reset the selected users pictures"))
    def clear_picture(self, request, queryset):
        """ Supprimer les images principales des profils """
        for profile in queryset:
            picture = profile.picture
            if picture is not None:
                profile.set_picture(None)
                picture.delete()

    @addattr(short_description=_(u"Shuffle profile"))
    def shuffle(self, request, queryset):
        """ Shuffle les données des profils"""
        for profile in queryset:
            shuffle_model(profile)
            profile.birth = random_date(ages_dates(18, 70))
            profile.save()

    # Overrides
    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut """
        qs = super(ProfileAdmin, self).get_queryset(request)
        field_list = ('user__username', 'user__id', 'picture', 'picture__id', 'picture__image', 'gender', 'birth', 'user__email', 'user__date_joined',)
        if apps.is_installed('location'):
            field_list += ('city__id',)
        qs = qs.select_related('user', 'picture').only(*field_list)
        return qs

    def get_autocomplete_queryset(self, request, field_name):
        """ Renvoyer le queryset utilisé pour autocomplete """
        if apps.is_installed('location') and field_name == 'city':
            from scoop.location.models import City
            # Uniquement les communes et villes
            return City.objects.filter(city=True)
        elif field_name == 'picture':
            from scoop.content.models import Picture
            # Toutes les images
            return Picture.objects.all()
        return None

    def get_form(self, request, obj=None, **kwargs):
        """ Renvoyer le formulaire utilisé pour l'admin """
        form = super(ProfileAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            form.base_fields['picture'].queryset = obj.pictures.all()
        return form

    # Getter
    @addattr(admin_order_field='user__id', short_description=_(u"Id"))
    def get_id(self, obj):
        """ Renvoyer l'ID de l'utilisateur """
        return obj.pk

    @addattr(short_description=_(u"User"), admin_order_field='user__username')
    def get_user(self, obj):
        """ Renvoyer l'utilisateur """
        return obj.user

    @addattr(admin_order_field='user__email', short_description=_(u"Email"))
    def get_email(self, obj):
        """ Renvoyer l'adresse email de l'utilisateur """
        return obj.user.email

    @addattr(allow_tags=True, admin_order_field='picture__title', short_description=_(u"User picture"))
    def get_image(self, obj):
        """ Renvoyer une vignette du portrait utilisateur """
        if obj.picture is not None:
            return "%s %sx%s" % (obj.picture.get_thumbnail_html(size=(48, 20)), obj.picture.width, obj.picture.height)


class ProfileAdminFormset(BaseInlineFormSet):
    """ Formset admin de profils """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formset """
        super(ProfileAdminFormset, self).__init__(*args, **kwargs)
        self.can_delete = False


class ProfileInlineAdmin(StackedInline):
    """ Inline d'administration de profil """
    model = get_profile_model()
    formset = ProfileAdminFormset
    formfield_overrides = {}
    template = 'admin/dating/profile/edit_inline/stacked.html'
    form = make_ajax_form(BaseProfile, {'city': 'citypm', 'picture': 'picture'}, ProfileInlineAdminForm)
    max_num = 2
    extra = 1
