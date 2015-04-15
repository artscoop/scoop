# coding: utf-8
from __future__ import absolute_import

import floppyforms as forms_
from annoying.decorators import autostrip
from django import forms
from django.template.defaultfilters import striptags
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE

from scoop.content.models import Content
from scoop.content.util.tinymce import TINYMCE_CONFIG_CONTENT
from scoop.core.forms.search import BaseSearchForm


@autostrip
class ContentForm(forms_.ModelForm):
    """ Formulaire de contenu """
    # Constantes
    TITLE_LENGTH_MIN = 4
    BODY_LENGTH_MIN = 32

    # Clean
    def clean_body(self):
        """ Valider et traiter le champ de texte """
        body = self.data['body']
        raw = striptags(body)
        if len(raw) < ContentForm.BODY_LENGTH_MIN:
            raise forms_.ValidationError(_(u"Your text must be at least {} characters long.").format(ContentForm.BODY_LENGTH_MIN))
        return body

    def clean_title(self):
        """ Valider et traiter le champ de titre """
        title = self.data['title']
        if len(title) < ContentForm.TITLE_LENGTH_MIN:
            raise forms_.ValidationError(_(u"The title must be at least {} characters long.").format(ContentForm.TITLE_LENGTH_MIN))
        return title

    # Métadonnées
    class Meta:
        model = Content
        widgets = {'title': forms_.TextInput(attrs={'size': 80}), 'body': TinyMCE(mce_attrs=TINYMCE_CONFIG_CONTENT)}
        exclude = ['content_type', 'object_id', 'similar', 'tags']
        fields = ['category', 'title', 'body', 'published', 'commentable', 'access']


@autostrip
class ContentAdminForm(forms.ModelForm):
    """ Formulaire admin de contenu """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(ContentAdminForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = Content
        widgets = {'title': forms.TextInput(attrs={'size': 80}), 'body': TinyMCE(mce_attrs=TINYMCE_CONFIG_CONTENT, attrs={'rows': 8})}
        exclude = []


@autostrip
class QuickContentForm(forms.ModelForm):
    """ Formulaire d'édition rapide de contenu """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(QuickContentForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = Content
        widgets = {'title': forms.TextInput(attrs={'size': 80, 'style': 'width:100%; height:30px; box-sizing:border-box; -moz-box-sizing:border-box'}),
                   'body': forms.Textarea(attrs={'rows': 5, 'style': 'width:100% !important; box-sizing:border-box; -moz-box-sizing:border-box'})}
        fields = ['title', 'body']


class ContentSearchForm(BaseSearchForm):
    """ Formulaire de recherche simple de contenu """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(ContentSearchForm, self).__init__(*args, **kwargs)
        self.Meta.base_qs = Content.objects

    # Métadonnées
    class Meta:
        base_qs = Content.objects
        search_fields = ['title']
