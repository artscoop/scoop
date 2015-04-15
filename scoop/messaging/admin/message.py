# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from django.contrib import admin
from django.forms.widgets import Textarea
from django.utils.translation import pgettext_lazy

from scoop.core.abstract.user.authored import AuthoredModelAdmin
from scoop.core.util.shortcuts import addattr
from scoop.messaging.forms import MessageAdminForm
from scoop.messaging.models.message import Message


class MessageAdmin(AuthoredModelAdmin):
    """ Administration des messages privés """
    list_select_related = True
    list_display = ('id', 'thread', 'get_author_link', 'name', 'text', 'deleted', 'is_spam', 'ip', 'get_position')
    list_display_links = ['id', 'thread']
    list_filter = ['deleted', 'spam']
    list_editable = ['deleted']
    readonly_fields = []
    search_fields = ['author__username', 'name', 'text', 'thread__topic']
    form = make_ajax_form(Message, {'author': 'user', 'thread': 'thread'}, MessageAdminForm)
    form.Meta.fields = MessageAdminForm.Meta.fields
    actions = []
    save_on_top = True
    actions_on_top = True
    raw_id_fields = []

    # Getter
    @addattr(short_description=pgettext_lazy('location', u"Location"))
    def get_position(self, obj):
        """ Renvoyer le lieu de l'IP du message """
        if obj.ip is not None and obj.ip.country:
            return u"{country} {city}".format(country=obj.ip.country, city=obj.ip.city_name)
        return None

    # Overrides
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Renvoyer le champ utilisé pour un formulaire du champ """
        if db_field.name == 'text':
            kwargs['widget'] = Textarea()
        return super(MessageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut de l'administration """
        qs = super(MessageAdmin, self).queryset(request)
        # qs = qs.select_related('author','thread','ip').only('author__username','author__id','id','thread__id','thread__topic','text','name','deleted','spam','ip__id','ip__string','ip__ip')
        return qs

# Enregistrer les classes d'administration
admin.site.register(Message, MessageAdmin)
