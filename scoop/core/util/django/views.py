# coding: utf-8
from django.http.response import HttpResponseBadRequest


def require_ajax(function):
    """
    Décorateur obligeant la requête à être une requête AJAX

    Renvoie une erreur HTTP 405 dans le cas contraire
    """

    def wrapped(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return function(request, *args, **kwargs)

    wrapped.__doc__ = function.__doc__
    wrapped.__name__ = function.__name__
    return wrapped
