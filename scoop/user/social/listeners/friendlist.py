# coding: utf-8
from django.dispatch.dispatcher import receiver
from scoop.user.social.util.signals import friend_pending_new


@receiver(friend_pending_new)
def new_friend_request(sender, recipient, **kwargs):
    """ Traiter une invitation à devenir ami avec un utilisateur  """
    pass
