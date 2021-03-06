# coding: utf-8
from django import forms
from django.template.defaultfilters import striptags
from django.utils.translation import ugettext_lazy as _
from scoop.content.models.comment import Comment


class CommentForm(forms.ModelForm):
    """ Formulaire de commentaires """

    # Constantes
    BODY_LENGTH_MIN = 8

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(CommentForm, self).__init__(*args, **kwargs)

    # Validation
    def clean_body(self):
        """ Valider le champ de texte """
        body = self.cleaned_data['body']
        actual_content = striptags(body)
        if len(actual_content) < CommentForm.BODY_LENGTH_MIN:
            raise forms.ValidationError(_("Your comment must be at least {length} characters long.").format(length=CommentForm.BODY_LENGTH_MIN))
        return body

    def clean(self):
        """ Valider le formulaire """
        data = super(CommentForm, self).clean()
        name, email, url = data['name'], data['email'], data['url']
        filled_count = (1 if name else 0) + (1 if email else 0) + (1 if url else 0)
        if filled_count < 3:  # Les 3 champs doivent être remplis
            raise forms.ValidationError(_("You must fill all fields."))

    # Métadonnées
    class Meta:
        model = Comment
        fields = ['body', 'url', 'email', 'name']
        widgets = {'body': forms.Textarea(attrs={'rows': 2})}

    # Médias
    class Media:
        pass


class CommentAdminForm(forms.ModelForm):
    """ Formulaire admin de commentaires """

    # Métadonnées
    class Meta:
        model = Comment
        fields = ['body', 'url', 'email', 'name', 'visible', 'content_type', 'object_id']
        widgets = {'body': forms.Textarea(attrs={'rows': 2})}
