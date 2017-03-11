# coding: utf-8
import datetime
import logging
import re
from random import randint
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import logout
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http.response import Http404, HttpResponse
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.utils import timezone
from scoop.core.util.shortcuts import get_qualified_name

logger = logging.getLogger('django_misery')

# Paramètres de Misery
logoutProbability = int(getattr(settings, 'MISERY_LOGOUT_PROBABILITY', 10))
e403Probability = int(getattr(settings, 'MISERY_403_PROBABILITY', 5))
e404Probability = int(getattr(settings, 'MISERY_404_PROBABILITY', 10))
whiteScreenProbability = int(getattr(settings, 'MISERY_WHITE_SCREEN_PROBABILITY', 15))
ASPdeathProbability = int(getattr(settings, 'MISERY_ASP_ERROR_PROBABILITY', 10))

# Vérifier les niveaux
assert 0 <= logoutProbability <= 100
assert 0 <= e403Probability <= 100
assert 0 <= e404Probability <= 100
assert 0 <= whiteScreenProbability <= 100
assert 0 <= ASPdeathProbability <= 100


class BanMiddleware(object):
    """ Ajouter une information de ban au cookie d'un banni """

    # Liste des répertoires à ne pas compter dans le logging
    RESOURCE_WHITELIST = {'media/', 'static/', '/ajax', '/admin/', '/manage/', '__debug'}
    BAN_COOKIE_NAME = 'client_bmid'  # ban marker id

    def process_request(self, request):
        """ Traiter la requête """
        if [i for i in BanMiddleware.RESOURCE_WHITELIST if i in request.path]:
            return
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated():
            banned = request.COOKIES.get(BanMiddleware.BAN_COOKIE_NAME, False)
            if banned is not False:
                user.profile.ban()

    def process_response(self, request, response):
        """ Traiter la réponse """
        if [i for i in BanMiddleware.RESOURCE_WHITELIST if i in request.path]:
            return response
        if hasattr(request, 'user'):
            user = request.user
            userid = user.pk or uuid4()
            if (hasattr(user, 'profile') and user.profile.banned):
                response.set_cookie(BanMiddleware.BAN_COOKIE_NAME, str(userid))
        return response


class MiserizeMiddleware(object):
    """
    Équivalent du module Drupal Misery
    Cause des problèmes de page aux membres inscrits et bannis.
    Permet de faire croire à l'utilisateur que le site a un problème et pas lui,
    ce qui dans de nombreux cas retardera l'utilisation de proxys ou encore d'un
    nouveau compte utilisateur.
    Le middleware cause plusieurs désagréments au hasard :
    - Long délai de réponse
    - 403, 404 et logouts intempestifs
    - Écrans vides
    - (Fausses) Erreurs ASP.net
    """

    def process_request(self, request):
        """ Traiter la requête """
        user = request.user
        if user.is_authenticated():
            profile = user.profile
            miserize = profile.is_banned()
            # Perturber l'activité utilisateur
            if miserize:
                logger.debug("{user} is miserized".format(user=user))

                # Tester sa chance sur un pourcentage de probabilité
                def out_of_luck(probability):
                    return randint(0, 100) >= probability

                # Tester les probabilités pour chaque désagrément
                if out_of_luck(logoutProbability):
                    logout(request)
                elif out_of_luck(e403Probability):
                    raise PermissionDenied()
                elif out_of_luck(e404Probability):
                    raise Http404()
                # Si post de formulaire, écran blanc une fois sur deux
                elif (request.has_post() and out_of_luck(whiteScreenProbability * 2)) or out_of_luck(whiteScreenProbability):
                    return HttpResponse("")
                elif out_of_luck(ASPdeathProbability):
                    return render_to_response('rogue/ban/ASPerror.html')
                    # Il est possible qu'aucun des cas précédents n'arrive


class LockMiddleware(object):
    """
    Bloquer un utilisateur temporairement

    Le rediriger vers une page l'avertissant qu'il est banni pendant n heures pour raison de comportement.
    """
    # Liste d'URLS où effectuer un blocage divin
    LOCK_TEMPLATE = "rogue/ban/temporary_lock.html"
    # Clé de cache. Contient un dictionnaire aux clés suivantes
    # - type : (int) raison du blocage
    # - expires : (datetime) date et heure de la fin du blocage
    # - views : (list:regex) regex des noms pleinement qualifiés de vues bloquées
    # - all : (bool) bloquer toutes les vues ou non
    # - all_post : (bool) bloquer tout dès qu'un POST est envoyé
    LOCK_KEY = 'pro.%d.templock'

    # Getter
    @staticmethod
    def get_lock(user):
        """ Renvoyer les informations de verrouillage """
        info = cache.get(LockMiddleware.LOCK_KEY % (user.pk,), None)
        return info

    @staticmethod
    def get_remaining_time(user):
        """ Renvoyer le temps de bannissement restant """
        info = cache.get(LockMiddleware.LOCK_KEY % (user.pk,), None)
        return (info['expires'] - timezone.now()).total_seconds() if info is not None else 0

    @staticmethod
    def is_locked(user):
        """ Renvoyer si un utilisateur est encore bloqué """
        return LockMiddleware.get_remaining_time(user) > 0

    # Setter
    @staticmethod
    def lock(user, duration=360, reason=0, views=None, all_views=False, all_post=False):
        """
        Bloquer un utilisateur
        :param duration: Durée du lock, en minutes
        """
        expiry = timezone.now() + datetime.timedelta(minutes=duration)
        info = {'type': reason, 'expires': expiry, 'views': views, 'all': all_views, 'all_post': all_post}
        cache.set(LockMiddleware.LOCK_KEY % (user.pk,), info, duration * 60)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Traiter la vue """
        user = request.user
        if user.is_authenticated() and user.is_active and not (user.is_staff or user.is_superuser):
            lock = LockMiddleware.get_lock(user)
            if lock is not None:
                locked = lock['all'] or (lock['all_post'] and request.has_post())
                if locked is False and lock['views'] is not None:
                    for regex in lock['views']:
                        locked |= re.match(regex, get_qualified_name(view_func), re.I) is not None
                if locked is True:
                    template = getattr(settings, 'LOCK_MIDDLEWARE_TEMPLATE', LockMiddleware.LOCK_TEMPLATE)
                    return render(request, template, {'lock': LockMiddleware.get_lock(user)})
