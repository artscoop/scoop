# coding: utf-8
from __future__ import absolute_import

import os
from zipfile import ZipFile

from captcha.fields import CaptchaField
from django import forms
from django.core.files.base import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.forms import widgets
from django.forms.models import modelformset_factory
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from form_utils.fields import ClearableImageField

from scoop.content.models.picture import Picture
from scoop.content.util.widgets import CreationLicenseWidget, PictureInlineWidget
from scoop.core.forms import BaseSearchForm


class PictureModelForm(forms.ModelForm):
    """ Formulaire d'images """
    # Champs
    image = ClearableImageField(widget=PictureInlineWidget, template=_("%(input)s Clear: %(checkbox)s"))

    def __init__(self, *args, **kwargs):
        """ Initialiser l'objet """
        super(PictureModelForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = Picture
        fields = ['image', 'title', 'description']
        widgets = {'image': PictureInlineWidget}


class PictureForm(forms.Form):
    """ Formulaire possédant un champ Image """
    picture = forms.ImageField()


class PictureAdminForm(forms.ModelForm):
    """ Formulaire admin des images """

    def __init__(self, *args, **kwargs):
        """ Initialiser l'objet """
        super(PictureAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['weight'].required = False
            self.fields['image'].required = False
            self.fields['image'].widget = PictureInlineWidget()
            self.fields['image'].help_text = _("You can also enter an URL as a Description.")
        except:
            pass

    def clean(self):
        """ Valider les données du formulaire et formater """
        cleaned_data = super(PictureAdminForm, self).clean()
        image = cleaned_data.get('image', '')
        url = cleaned_data.get('description', '').strip()
        scheme = Picture._parse_scheme(url)
        if not image and (not url or (url and scheme not in ['http', 'https', 'find', 'file'])):
            raise forms.ValidationError(_("You must specify an image or put an URL as a description"))
        return cleaned_data

    # Métadonnées
    class Meta:
        model = Picture
        fields = ['image', 'title', 'description', 'weight', 'author', 'content_type', 'object_id', 'license', 'audience']
        formfield_overrides = {models.ImageField: {'widget': PictureInlineWidget}, models.TextField: {'widget': widgets.Input(attrs={'maxlength': 1024})}}
        widgets = {'license': CreationLicenseWidget}


class PictureAdminInlineForm(PictureAdminForm):
    """ Formulaire inline admin des Images """

    # Métadonnées
    class Meta:
        model = Picture
        fields = ['image', 'description', 'weight']


class PictureSearchForm(BaseSearchForm):
    """ Formulaire de recherche d'images """

    def __init__(self, *args, **kwargs):
        """ Initialiser l'objet """
        super(PictureSearchForm, self).__init__(*args, **kwargs)
        self.Meta.base_qs = Picture.objects

    # Métadonnées
    class Meta:
        base_qs = Picture.objects
        search_fields = ['title', 'description', 'image']


class ZipUploadForm(forms.Form):
    """ Formulaire d'upload d'archive ZIP d'images """
    zipfile = forms.FileField(max_length=128, label=_("Zip archive"))
    captcha = CaptchaField()

    def clean_zipfile(self):
        """ Renvoyer le fichier uploadé """
        datafile = self.files.get('zipfile', None)
        return datafile

    def clean(self):
        """ Valider le formulaire """
        datafile = self.clean_zipfile()
        if datafile is None:
            raise forms.ValidationError(_("File must be a zip file"))
        return self.cleaned_data

    def save_file(self, datafile):
        """ Ouvrir le fichier uploadé et créer les images contenues """
        if isinstance(datafile, str):
            datafile = open(datafile, 'r')
        content_type = datafile.content_type
        if content_type in {'application/zip', 'application/x-zip-compressed'}:
            archive = ZipFile(datafile, 'r')
            names = archive.namelist()
            for name in names:
                filename, fileext = os.path.splitext(name.lower())
                if fileext in ['.png', '.jpg', '.jpeg']:
                    item = archive.open(name)
                    with NamedTemporaryFile(prefix=slugify(filename), suffix=fileext, delete=False) as tfile:
                        tfile.write(item.read())
                        picture = Picture(author=self.request.user)
                        picture.image.save(tfile.name, File(tfile))
                        picture.save()
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("File must be a zip file"))

    # Overrides
    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        self.request = kwargs.pop('request', None)
        super(ZipUploadForm, self).__init__(*args, **kwargs)

# Formulaire multiple d'images
PictureFormSet = modelformset_factory(Picture, form=PictureModelForm, extra=2)
