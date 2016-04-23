# coding: utf-8
import functools

from django.contrib.auth import get_user_model
from django.http import Http404
from scoop.messaging.models.thread import Thread


def user_can_see_thread(method):
    """
    Décorateur vérifiant que l'utilisateur fait partie d'un thread
    La fonction décorée peut être de la forme suivante :
    - func(thread, ...) où thread est un objet Thread en premier argument
    - func(request, ... uuid ...). uuid est un kwarg et non un arg, selon urls.py
    """

    @functools.wraps(method)
    def wrapper(request, *args, **kwargs):
        thread = None
        if kwargs.get('uuid', None) is not None:
            thread = Thread.objects.get_by_uuid(kwargs.get('uuid'))
        elif len(args) > 0 and isinstance(args[0], Thread):
            thread = args[0]
        if thread is None or request.user.is_anonymous() or not thread.is_recipient(request.user):
            raise Http404()
        return method(request, *args, **kwargs)

    return wrapper


def user_can_see_inbox(method):
    """
    Décorateur vérifiant que l'utilisateur peut consulter une inbox
    La fonction décorée peut être de la forme suivante :
    - func(request, ... uuid ...). uuid est un kwarg et non un arg, selon urls.py
    """

    @functools.wraps(method)
    def wrapper(request, *args, **kwargs):
        uuid = kwargs.get('uuid', None)
        user = request.user
        if uuid is not None:
            user = get_user_model().objects.get_by_uuid(uuid, request.user)
        elif len(args) > 0 and isinstance(args[0], get_user_model()):
            user = args[0]
        if user is None or user.is_anonymous() or not request.user.can_edit(user) or request.user.is_anonymous():
            raise Http404()
        return method(request, *args, **kwargs)

    return wrapper


def user_can_send_to(method):
    """ Décorateur vérifiant que l'utilisateur peut envoyer un message à un autre """

    @functools.wraps(method)
    def wrapper(request, *args, **kwargs):
        uuid = kwargs.get('uuid', None)
        user = request.user
        if uuid is not None:
            user = get_user_model().objects.get_by_uuid(uuid, request.user)
        elif len(args) > 0 and isinstance(args[0], get_user_model()):
            user = args[0]
        # Si la simulation de nouveau thread échoue, alors renvoyer un 404
        if Thread.objects.simulate(request.user, [user]) is False:
            raise Http404()
        return method(request, *args, **kwargs)

    return wrapper
