# coding: utf-8
from ajax_select.helpers import make_ajax_field
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from scoop.content.models.album import Album, AlbumPicture
from scoop.core.util.model.model import limit_to_model_names


class AlbumForm(forms.ModelForm):
    """ Formulaire d'albums """

    # Constantes
    NAME_LENGTH_MIN = 2
    DEFAULT_NAME = _("{author}'s album")

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(AlbumForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].queryset = ContentType.objects.filter(limit_to_model_names('content.content', 'user.user'))

    # Métadonnées
    class Meta:
        model = Album
        fields = ['name']


class AlbumAdminForm(AlbumForm):
    """ Formulaire admin des albums """

    # Métadonnées
    class Meta:
        model = Album
        exclude = []


class AlbumPictureAdminInlineForm(forms.ModelForm):
    """ Formulaire inline des images des albums """

    picture = make_ajax_field(AlbumPicture, 'picture', 'picture')

    class Meta:
        model = AlbumPicture
        fields = ['picture', 'weight', 'notes']


# Formulaire multiple d'images
AlbumPictureFormSet = modelformset_factory(AlbumPicture, form=AlbumPictureAdminInlineForm, extra=2)
