# coding: utf-8
from django import forms
from scoop.content.util.tinymce import TINYMCE_CONFIG_CONTENT
from scoop.editorial.models.configuration import Configuration
from scoop.editorial.models.excerpt import ExcerptTranslation
from tinymce.widgets import TinyMCE


class ConfigurationInlineForm(forms.ModelForm):
    """ Formulaire de configurations """

    # Métadonnées
    class Meta:
        model = Configuration
        exclude = ['time']


class ExcerptTranslationInlineForm(forms.ModelForm):
    """ Formulaire inline des extraits """

    # Métadonnées
    class Meta:
        model = ExcerptTranslation
        widgets = {'text': TinyMCE(mce_attrs=TINYMCE_CONFIG_CONTENT)}
        exclude = []
