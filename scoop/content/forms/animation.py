# coding: utf-8
import os
from zipfile import ZipFile

from django import forms
from django.core.files.base import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.forms import widgets
from django.forms.models import modelformset_factory
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from form_utils.fields import ClearableImageField
from rarfile import RarFile

from scoop.content.models.animation import Animation
from scoop.content.models.picture import Picture
from scoop.content.util.widgets import CreationLicenseWidget, PictureInlineWidget
from scoop.core.forms import BaseSearchForm

try:
    from captcha.fields import CaptchaField
except RuntimeError:
    def CaptchaField():
        return None


class AnimationForm(forms.ModelForm):
    """ Formulaire d'animations """

    def __init__(self, *args, **kwargs):
        """ Initialiser l'objet """
        super(AnimationForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = Animation
        fields = ['file', 'title', 'acl_mode', 'author', 'picture']
