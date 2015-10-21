# coding: utf-8
from __future__ import absolute_import

import floppyforms as forms
from django import forms as baseforms
from django.contrib.auth import get_user_model
from django.template.defaultfilters import striptags
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE

from scoop.content.util.tinymce import TINYMCE_CONFIG_CONTENT
from scoop.core.util.model.widgets import SelectDateWidget
from scoop.messaging.models.message import Message
from scoop.messaging.models.recipient import Recipient
from scoop.messaging.models.thread import Thread


class MessageForm(forms.Form):
    """ Formulaire de message """
    # Constantes
    BODY_LENGTH_MIN = 2
    HELP_TEXT = _("Please make use of polite and correct language and behaviour.")
    INPUT_CSS = "width: 100%; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box;"
    # Champs
    body = forms.CharField(required=False, label="", help_text=HELP_TEXT,
                           widget=TinyMCE(attrs={'rows': 3}, mce_attrs=TINYMCE_CONFIG_CONTENT))  # widget=Textarea(attrs={'style':INPUT_CSS, 'rows':3}))

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(MessageForm, self).__init__(*args, **kwargs)

    # Validation
    def clean_body(self):
        """ Valider et renvoyer les données du champ texte """
        body = self.data['body']
        raw = striptags(body)
        if len(raw) < MessageForm.BODY_LENGTH_MIN:
            raise forms.ValidationError(_("Your message must be at least {} characters long.").format(MessageForm.BODY_LENGTH_MIN))
        return body


class ThreadForm(MessageForm):
    """ Formulaire de fil de discussion """
    # Constantes
    SUBJECT_LENGTH_MIN = 1
    # Champs supplémentaires
    subject = forms.CharField(max_length=48, required=False, widget=forms.TextInput())
    recipient = forms.IntegerField(required=True, widget=forms.HiddenInput())

    # Validation
    def clean_subject(self):
        """ Valider et renvoyer les données du champ sujet """
        subject = self.data['subject']
        if len(subject) < ThreadForm.SUBJECT_LENGTH_MIN:
            raise forms.ValidationError(_("Your subject must be at least {} characters long.").format(ThreadForm.SUBJECT_LENGTH_MIN))
        return subject

    def clean_recipient(self):
        """ Valider et renvoyer les données du champ destinataire """
        recipient = int(self.data['recipient'])
        if get_user_model().objects.get_or_none(id=recipient) is None:
            raise forms.ValidationError(_("The recipient does not exist."))
        return get_user_model().objects.get(id=recipient)


class MessageAdminForm(baseforms.ModelForm):
    """ Formulaire admin des messages """

    # Métadonnées
    class Meta:
        model = Message
        widgets = {'text': forms.TextInput(attrs={'size': 80})}
        fields = ['thread', 'author', 'text', 'deleted']


class ThreadAdminForm(forms.ModelForm):
    """ Formulaire admin des threads """

    # Métadonnées
    class Meta:
        model = Thread
        exclude = []


class RecipientAdminForm(forms.ModelForm):
    """ Formulaire admin des destinataires """

    # Métadonnées
    class Meta:
        model = Recipient
        fields = ['thread', 'user', 'active']


class MessageSearchForm(forms.Form):
    """ Formulaire de recherche de messages """
    query = forms.CharField(max_length=128, required=False)
    ip = forms.GenericIPAddressField(required=False)
    q = forms.CharField(max_length=48, required=False)
    when = forms.DateTimeField(widget=SelectDateWidget(years=range(2010, 2012)))
