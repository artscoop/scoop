# coding: utf-8
import datetime

from ajax_select import make_ajax_form
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.model.widgets import AdminSplitDateTime
from scoop.core.util.shortcuts import addattr
from scoop.messaging.forms.thread import ThreadAdminForm
from scoop.messaging.models.thread import Thread


class ThreadAdmin(admin.ModelAdmin):
    """ Administration des fils de discussion """
    list_select_related = True
    list_display = ['id', 'topic', 'author', 'get_recipient_pictures', 'get_message_count', 'get_started', 'get_updated', 'deleted', 'closed', 'get_expires',
                    'get_label_count']
    list_filter = ['started', 'deleted', 'closed']
    list_display_links = ['id', 'topic']
    search_fields = ['topic', 'recipients__user__username']
    readonly_fields = ['started', 'updated']
    exclude = ['counter']
    actions = []
    form = make_ajax_form(Thread, {'author': 'user'}, ThreadAdminForm)
    inlines = []
    save_on_top = False
    actions_on_top = True
    fieldsets = (
    (_("Thread"), {'fields': ('author', 'topic', 'deleted', 'closed')}), (_("Expiry"), {'fields': ('expires', 'expiry_on_read', 'started', 'updated')}),)
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'

    # Getter
    @addattr(short_description=_("Recipients"))
    def get_recipients(self, obj):
        """ Renvoyer la liste des destinataires """
        return ", ".join(["{}".format(item.user.username) for item in obj.recipients.all()])

    @addattr(allow_tags=True, short_description=_("Recipients"))
    def get_recipient_pictures(self, obj):
        """ Renvoyer les vignettes des destinataires """
        picture_links = []
        for recipient in obj.get_users(exclude=obj.author):
            picture_links.append("""<a href="{}">{}</a>""".format(recipient.get_absolute_url(), recipient))
        return " ".join(picture_links)

    @addattr(short_description=_("Expiry on read"))
    def get_expiry(self, obj):
        """ Renvoyer l'expiration après lecture """
        delta = datetime.timedelta(days=obj.expiry_on_read)
        return delta

    @addattr(admin_order_field='expires', short_description=_("Expires"))
    def get_expires(self, obj):
        """ Renvoyer la date d'expiration du fil de discussion """
        return obj.expires or _("Never")

    @addattr(admin_order_field='started', short_description=_("Was started"))
    def get_started(self, obj):
        """ Renvoyer la date de début du fil de discussion """
        return obj.started.strftime("%d/%m/%Y %H:%M")

    @addattr(admin_order_field='updated', short_description=_("Updated"))
    def get_updated(self, obj):
        """ Renvoyer la date de modification de la discussion """
        return obj.updated.strftime("%d/%m/%Y %H:%M")

    # Overrides
    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut de l'administration """
        qs = super(ThreadAdmin, self).get_queryset(request)
        qs = qs.select_related('author').only('author__username', 'author__id', 'id', 'topic', 'started', 'deleted', 'updated', 'closed', 'expires')
        return qs

    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Renvoyer le champ de formulaire pour un champ """
        if db_field.name == 'expires':
            kwargs['widget'] = AdminSplitDateTime()
        return super(ThreadAdmin, self).formfield_for_dbfield(db_field, **kwargs)


# Enregistrer les classes d'administration
admin.site.register(Thread, ThreadAdmin)
