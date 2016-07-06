# coding: utf-8
import celery
from django.core.handlers.wsgi import WSGIRequest
from django.http.request import HttpRequest
from waffle import switch_is_active

from scoop.core.util.stream.request import RequestMixin


@celery.task(name='user.access.log_access', ignore_result=True, expires=86400)
def add_access(request):
    """
    Ajouter une entrée au log des accès

    :param request: objet HttpRequest
    """
    from scoop.user.access.models.access import Access
    if switch_is_active('access.log') and request:
        return Access.objects.add(request)
