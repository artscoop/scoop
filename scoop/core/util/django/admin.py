# coding: utf-8
import inspect

from django.contrib import admin
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.contenttypes.fields import ContentType
from django.core.urlresolvers import reverse_lazy as reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext
from scoop.core.util.shortcuts import addattr


class GenericModelUtil():
    """ Mixin d'administration pour les objets avec un lien générique """

    @addattr(allow_tags=True, admin_order_field='content_type', short_description=_("Target"))
    def get_content_object_info(self, obj):
        """ Renvoyer un lien vers la page d'admin de l'objet lié """
        admin_link = []
        if obj.content_object is not None:
            if hasattr(obj.content_object, '__html__'):
                admin_link.append(''.join([obj.content_object.__html__(), '&nbsp;' * 3]))
            if hasattr(obj.content_object, 'get_admin_url'):
                admin_link.append('<a href="%s">%s</a>' % (obj.content_object.get_admin_url(), obj.content_object.__str__()))
            return "".join(admin_link)
        return "<em class='muted'>%s</em>" % (pgettext('target', "None"),)

    @addattr(allow_tags=True, admin_order_field='content_type', short_description=_("Type"))
    def get_content_type_info(self, obj):
        """ Renvoyer un lien vers la gestion du Modèle de la cible """
        css = 'label-info' if obj.content_type else ''
        url = '#' if not hasattr(obj.content_type, 'get_admin_url') else obj.content_type.get_admin_url()
        label = obj.content_type or pgettext('type', "None")
        tag = 'a' if obj.content_type else 'span'
        return '<%s href="%s"><span class="label %s">%s</span></%s>' % (tag, url, css, label, tag)


class AdminURLUtil():
    """
    Mixin de modèle avec une fonction pour connaître la page d'admin de l'objet
    Monkey-patching done in scoop.core.__init__
    """

    def get_admin_url(self):
        """ Renvoyer l'URL d'admin du modèle """
        try:
            if not inspect.isclass(self) and not isinstance(self, ContentType):
                content_type = ContentType.objects.get_for_model(self)
                url = reverse('admin:%s_%s_change' % (content_type.app_label, content_type.model), args=[self.id])
            else:
                url = reverse('admin:%s_%s_changelist' % (self.app_label, self.model))
            return url
        except:
            return "/"


class ViewOnlyModelAdmin(admin.ModelAdmin):
    """ Mixin d'administration empêchant toute modification """

    def has_delete_permission(self, request, obj=None):
        """ Impossible de supprimer des objets """
        return False

    def has_add_permission(self, request):
        """ Impossible d'ajouter des objets """
        return False


def _boolean_icon(field_val):
    """ Remplacer les icônes .gif de l'administration par des .png """
    icon_url = static('admin/img/icon-%s.png' % {True: 'yes', False: 'no', None: 'unknown'}[field_val])
    return mark_safe('<img src="%s" alt="%s" />' % (icon_url, field_val))
