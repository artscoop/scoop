# coding: utf-8
from __future__ import absolute_import

from django.contrib import admin
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from scoop.core.admin.filters import TimestampFilter
from scoop.core.templatetags.text_tags import truncate_ellipsis
from scoop.core.util.shortcuts import addattr
from scoop.user.models.forms import FormConfiguration

__all__ = ['ConfigurationAdmin']


class ConfigurationAdmin(admin.ModelAdmin):
    """ Administration des configurations de formulaire utilisateur """
    list_select_related = True
    list_display = ['id', 'user', 'name', 'get_version', 'get_data', 'get_datetime_format']
    list_filter = ['name', 'version', TimestampFilter]
    list_editable = []
    list_per_page = 25
    search_fields = ['uuid']
    ordering = ['-time']
    actions = []

    # Getter
    @addattr(admin_order_field='version', short_description=_("Version"))
    def get_version(self, obj):
        """ Renvoyer la version de la configuration """
        return obj.version or _("Default")

    @addattr(allow_tags=True, admin_order_field='data', short_description=_("Data"))
    def get_data(self, obj):
        """ Renvoyer la représentation HTML des données de configuration """
        output = """<span title="{data}">{text}</span>""".format(data=escape(obj.data), text=truncate_ellipsis(str(obj.data), 40))
        return output

# Enregistrer les classes d'administration
admin.site.register(FormConfiguration, ConfigurationAdmin)
