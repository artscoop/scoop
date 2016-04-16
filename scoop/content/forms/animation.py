# coding: utf-8

from django import forms

from scoop.content.models.animation import Animation


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
