# coding: utf-8
from django import forms
from easy_thumbnails.fields import ThumbnailerImageField
from scoop.content.util.widgets import PictureInlineWidget
from scoop.forum.models.forum import Forum


class ForumAdminForm(forms.ModelForm):
    """ Formulaire admin des forums """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(ForumAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['icon'].widget = PictureInlineWidget()
        except:
            pass

    # Métadonnées
    class Meta:
        model = Forum
        formfield_overrides = {ThumbnailerImageField: {'widget': PictureInlineWidget}}
        exclude = []
