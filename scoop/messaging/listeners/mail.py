# coding: utf-8
from django.contrib.auth.signals import user_logged_in
from django.dispatch.dispatcher import receiver
from scoop.messaging.models import MailEvent, MailType
from scoop.messaging.util.signals import mailable_event
from scoop.user.forms.configuration import ConfigurationForm


@receiver(mailable_event)
def default_mail_send(sender, mailtype, recipient, data, **kwargs):
    """
    Traiter la mise en file d'un nouvel événement mail

    Certains mails peuvent ne pas être envoyés dans les cas suivants :
    - L'utilisateur est en ligne et le mail est spécifique au hors-ligne
    Certains mails sont toujours envoyés :
    - Les mails avec un type dit forcé (avec une catégorie "important")
    :param recipient: L'adresse email ou l'utilisateur cible
    :type mailtype: str | MailType
    :type recipient: str | User
    """
    category_option = {'message': 'receive_on_message', 'staff': 'receive_on_staff', 'subscription': 'receive_on_scubscription'}

    # Récupérer l'obet MailType correspondant au mailtype passé
    mailtype = MailType.objects.get_named(mailtype) if isinstance(mailtype, str) else mailtype
    categories = mailtype.get_categories()
    # Recenser les cas où le mail peut, doit ou ne peut pas être envoyé
    chose_to_receive = any([ConfigurationForm.get_option_for(recipient, category_option[category]) for category in categories if category in category_option])
    can_receive = all([category not in category_option for category in categories])  # Si aucune catégorie correspond à une option autoriser par défaut
    must_receive = mailtype.has_category('important')
    restrict_online = False
    if not isinstance(recipient, str):
        restrict_online = recipient.is_active and recipient.is_online(600) and not mailtype.has_category('online')
    # Si le mail doit, ou peut être envoyé, ajouter en file
    if must_receive or ((chose_to_receive or can_receive) and not restrict_online):
        MailEvent.objects.queue(recipient, mailtype.short_name, data, forced=must_receive)


@receiver(user_logged_in)
def clear_offline_mailevents(sender, request, user, **kwargs):
    """ Supprimer les événements mails supprimables si l'utilisateur est en ligne """
    MailEvent.objects.discardable(user).discard()
