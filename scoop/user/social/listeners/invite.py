# coding: utf-8
from django.dispatch.dispatcher import receiver
from scoop.user.social.models.group import Group
from scoop.user.social.util.signals import invite_accepted


@receiver(invite_accepted, sender=Group)
def group_invite_accepted(sender, instance, **kwargs):
    """ Traiter une invitation à un groupe acceptée """
    # Marquer l'invitation comme acceptée
    instance.update(save=True, status=1)  # Accepté
    # Ajouter l'invité aux membres du groupe
    group = instance.content_object
    group.add_member(instance.target)
