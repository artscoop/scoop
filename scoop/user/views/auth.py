# coding: utf-8
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse_lazy as reverse
from django.http import HttpResponseRedirect
from scoop.user.models.activation import Activation
from scoop.user.models.user import User
from scoop.user.util.auth import is_authenticated


@user_passes_test(is_authenticated)
def logout(request):
    """ Déconnecter un utilisateur """
    target = request.REQUEST.get('next', reverse('index'))
    User.sign(request, None, logout=True)
    return HttpResponseRedirect(target)


def profile_activate(request, username=None, uuid=None):
    """ Tenter d'activer un nouvel utilisateur """
    Activation.objects.activate(uuid, username, request)  # envoie un signal en cas de succès ou d'échec
    target = request.REQUEST.get('next', reverse('index'))
    return HttpResponseRedirect(target)
