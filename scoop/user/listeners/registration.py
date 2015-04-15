# coding: utf-8
from __future__ import absolute_import

from django.dispatch.dispatcher import receiver

from scoop.user.util.signals import credentials_form_check_name


@receiver(credentials_form_check_name)
def form_check_name(sender, name, **kwargs):
    """ Vérifier le champ nom d'un formulaire utilisateur """
    pass
