# coding: utf-8
from __future__ import absolute_import

import logging

from django.core.exceptions import ValidationError
from django.dispatch.dispatcher import receiver

from scoop.user.util.signals import credentials_form_check_email

logger = logging.getLogger(__name__)


@receiver(credentials_form_check_email)
def check_form_email(sender, mail, **kwargs):
    """ Vérifier la validité d'un champ email """
    from scoop.rogue.models.mailblock import MailBlock
    # Adresse non autorisée
    if MailBlock.objects.is_blocked(mail):
        raise ValidationError("This email address is not authorized.")
    return True
