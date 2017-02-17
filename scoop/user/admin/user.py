# coding: utf-8
import locale

from ajax_select import make_ajax_form
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy as reverse
from django.template.defaultfilters import escape
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.shortcuts import addattr
from scoop.user.admin.filters import InitialFilter, LastOnlineFilter, OnlineFilter
from scoop.user.admin.profile import ProfileInlineAdmin
from scoop.user.forms.user import UserAdminForm

__all__ = ['UserAdmin']


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    """ Administration des utilisateurs """
    list_select_related = True
    list_display = ['id', 'get_uuid_html', 'username', 'get_image', 'get_profile_link', 'email', 'is_active', 'is_online', 'get_joined_date', 'get_last_online']
    list_filter = ['is_active', OnlineFilter, LastOnlineFilter, 'is_staff', 'is_superuser', 'groups', InitialFilter]
    list_display_links = ['id', 'username']
    list_editable = []
    list_per_page = 25
    search_fields = ['username', 'email', 'id']
    exclude = ('last_login',)
    fieldsets = ((_("User"), {'fields': ('username', 'email', 'password', 'name')}),
                 (_("Status"), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
                 (_("Plus"), {'fields': ('next_mail',)})
                 )
    form = make_ajax_form(get_user_model(), {'user_permissions': 'permission', 'groups': 'group'}, UserAdminForm)
    inlines = [ProfileInlineAdmin]
    save_on_top = False
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    actions = ['deactivate', 'logout']

    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')  # Définir la langue locale

    # Actions
    @addattr(short_description=_("Deactivate selected users"))
    def deactivate(self, request, queryset):
        """ Désactiver des utilisateurs """
        count = queryset.update(is_active=False)
        self.message_user(request, _("{count} users have been successfully deactivated.").format(count=count), messages.SUCCESS)

    @addattr(short_description=_("Disconnect selected users"))
    def logout(self, request, queryset):
        """ Forcer la déconnexion des utilisateurs """
        for user in queryset:
            if user.profile:
                user.profile.force_logout()
        self.message_user(request, _("{count} users have been successfully logged out.").format(count=queryset.count()), messages.SUCCESS)

    # Getter
    @addattr(admin_order_field='date_joined', short_description=_("date joined"))
    def get_joined_date(self, obj):
        """ Renvoyer la date d'inscription """
        return obj.date_joined.strftime('%d %b %Y %H:%M')

    @addattr(admin_order_field='last_login', short_description=_("last login"))
    def get_last_login(self, obj):
        """ Renvoyer la date de dernière connexion """
        if obj.last_login:
            return obj.last_login.strftime('%d %b %Y %H:%M')
        else:
            return "None"

    @addattr(admin_order_field='last_online', short_description=_("last online"))
    def get_last_online(self, obj):
        """ Renvoyer la date où l'utilisateur a été vu en ligne la dernière fois """
        if obj.last_online:
            return obj.last_online.strftime('%d %b %Y %H:%M')
        return _("Never")

    def related_count(self, obj):
        """ Renvoyer le nombre d'objet liés à l'utilisateur (FK et M2M) """
        return len(obj.get_all_related_objects())

    @addattr(short_description=_("Groups"))
    def get_groups(self, obj):
        """ Renvoyer les groupes de l'utilisateur """
        groups = obj.groups.all()
        output = _("(None)")
        if groups.exists():
            output = ", ".join([group.name for group in groups])
        return output

    @addattr(allow_tags=True, short_description=_("Profile"))
    def get_profile_link(self, obj):
        """ Renvoyer un lien vers la page d'admin du profil """
        return """<a href="{}">{}</a>""".format(reverse("admin:dating_profile_change", args=(obj.profile.user_id,)), escape(obj.profile.__str__()))

    @addattr(allow_tags=True, short_description=_("User picture"))
    def get_image(self, obj):
        """ Renvoyer une vignette de l'image de profil de l'utilisateur """
        if obj.profile.picture is not None:
            return "{} <small>{}x{}</small>".format(obj.profile.picture.get_thumbnail_html(size=(48, 20)), obj.profile.picture.width,
                                                    obj.profile.picture.height)
