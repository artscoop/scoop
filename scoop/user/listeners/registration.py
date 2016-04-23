# coding: utf-8
from django.core.exceptions import ValidationError
from django.dispatch.dispatcher import receiver
from scoop.user.util.signals import credentials_form_check_email, credentials_form_check_name


@receiver(credentials_form_check_name)
def form_check_name(sender, name, **kwargs):
    """ Vérifier le champ nom d'un formulaire utilisateur """
    from scoop.rogue.models import Profanity
    if Profanity.objects.get_profanities_for(name):
        raise ValidationError("This name is not allowed")


@receiver(credentials_form_check_email)
def form_check_email(sender, email, **kwargs):
    """ Vérifier le champ email d'un formulaire utilisateur """
    from scoop.rogue.models import MailBlock
    if MailBlock.objects.is_blocked(email):
        raise ValidationError("This email is not allowed")
