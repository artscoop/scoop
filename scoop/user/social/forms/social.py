# coding: utf-8
from django import forms


class PostForm(forms.Form):
    """ Formulaire de posts """
    post = forms.CharField(max_length=160)


class PostCommentForm(forms.Form):
    """ Formulaire de commentaires de posts """
    comment = forms.CharField(max_length=160, min_length=1)
