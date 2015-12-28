# coding: utf-8
from django import forms
from scoop.content.models import Category


class CategoryForm(forms.Form):
    """ Formulaire de choix du type de contenu """
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = kwargs.get('queryset', self.fields['category'].queryset)
