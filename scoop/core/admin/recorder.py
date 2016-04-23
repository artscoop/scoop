# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from scoop.core.models.recorder import ActionType, Record
from scoop.core.util.shortcuts import addattr


class ActionTypeAdmin(admin.ModelAdmin):
    """ Administration des types d'actions du recorder """
    list_select_related = True
    list_display = ['id', 'get_color_legend', 'get_codename', 'is_valid', 'get_sentence', 'verb', 'get_record_count']
    list_display_links = []
    list_filter = []
    list_editable = []
    readonly_fields = []
    search_fields = ['codename', 'sentence']
    actions = []
    exclude = []
    actions_on_top = True
    order_by = ['codename']

    # Getter
    @addattr(short_description=_("Record count"))
    def get_record_count(self, obj):
        """ Renvoyer le nombre d'actions du même type """
        count = Record.objects.filter(type=obj).count()
        return count

    @addattr(allow_tags=True, admin_order_field='codename', short_description=_("Codename"))
    def get_codename(self, obj):
        """ Renvoyer une représentation HTML du nom de code de l'objet """
        codeparts = obj.codename.split('.')
        output = "<strong class='text-info'>%(app)s</strong> &#8226; " % {'app': codeparts.pop(0)}
        output += " &#8226; ".join(codeparts)
        return output

    @addattr(allow_tags=True, admin_order_field='sentence', short_description=_("Sentence"))
    def get_sentence(self, obj):
        """ Renvoyer une représentation HTML de la description de l'action """
        sentence = obj.sentence
        sentence = sentence.replace('%(actor)s', '<strong class="text-info">actor</strong>')
        sentence = sentence.replace('%(container)s', '<strong class="text-info">container</strong>')
        sentence = sentence.replace('%(target)s', '<strong class="text-info">target</strong>')
        return sentence


class RecordAdmin(admin.ModelAdmin):
    """ Administration des enregistrements d'actions """
    list_select_related = True
    list_display = ['id', 'get_color_legend', 'get_datetime_ago', 'user', 'type', 'target_object', 'container_object', 'description']
    list_display_links = []
    list_filter = ['type']
    list_editable = []
    readonly_fields = []
    search_fields = ['type__codename', 'type__sentence']
    actions = []
    exclude = []
    actions_on_top = True
    order_by = ['id']


# Enregistrer les classes d'administration
admin.site.register(ActionType, ActionTypeAdmin)
admin.site.register(Record, RecordAdmin)
