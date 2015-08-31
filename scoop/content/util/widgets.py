# coding: utf-8
from __future__ import absolute_import

from django import forms
from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy


class PictureInlineWidget(forms.FileInput):
    """ Widget d'upload d'images """

    def __init__(self, attrs={}):
        super(PictureInlineWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        """ Rendre le widget """
        widget = super(PictureInlineWidget, self).render(name, value, attrs)
        output = render_to_string("content/display/picture/widget/inline.html", {'widget': widget, 'image': value})
        return mark_safe(output)


class InlineWidget(forms.Widget):
    """ Widget d'insertion d'inlines """

    def __init__(self, attrs={}):
        """ Inititaliser """
        super(InlineWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        """ Rendre le widget """
        output = render_to_string("content/inlines/widget/picture.html", {'value': value})
        return mark_safe(output)


class CreationLicenseWidget(forms.MultiWidget):
    """ Widget de licence ou copyright """
    # Constantes
    COPYRIGHTED = {1: _("Copyright")}
    CREATIVE_COMMONS = {10: _("CC BY - Attribution"), 11: _("CC BY-SA - Share alike"), 12: _("CC BY-ND - Cannot edit"), 13: _("CC BY-NC - Non commercial"), 14: _("CC BY-NC-SA - SA+NC"),
                        15: _("CC BY-NC-ND - ND+NC"), 16: _("Public domain")}

    def __init__(self, attrs=None, widget=None):
        """ Initialiser le widget """
        license_widget = widgets.Select if not widget else widget
        license_widget = license_widget(choices=CreationLicenseWidget.get_choices(), attrs={u'class': u'license-license', u'style': u'min-width: 24em;'})
        _widgets = (license_widget, widgets.TextInput(attrs={u'class': u'license-author', u'placeholder': _("Creator or rights holder")}))
        super(CreationLicenseWidget, self).__init__(_widgets, attrs)

    # Getter
    @staticmethod
    def get_choices():
        """ Renvoyer les choix de licences disponibles """
        cc_choices = [[0, pgettext_lazy('license', "None")], [_("Creative Commons"), CreationLicenseWidget.CREATIVE_COMMONS.items()],
                      [_("Copyright"), CreationLicenseWidget.COPYRIGHTED.items()]]
        return cc_choices

    def decompress(self, value):
        """ Renvoyer un objet python depuis une chaîne """
        if value:
            licens, author = value.split(';', 1)
            licens = licens or None
            return [licens, author]
        return [None, ""]

    def value_from_datadict(self, data, files, name):
        """ Renvoyer la chaîne de licence depuis des données de formulaire """
        data = [widget.value_from_datadict(data, files, "{}_{}".format(name, i)) for i, widget in enumerate(self.widgets)]
        licens = data[0] or ''
        author = data[1]
        return "{};{}".format(licens, author)

    def format_output(self, rendered_widgets):
        """ Renvoyer le rendu des sous-widgets du widget """
        return u' '.join(rendered_widgets)
