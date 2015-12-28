# coding: utf-8
import celery
from waffle import switch_is_active


@celery.task(name='user.access.log_access', ignore_result=True)
def add_access(request):
    """ Ajouter une entrée au log des accès """
    from scoop.user.access.models.access import Access
    if switch_is_active('access.log') and request:
        return Access.objects.add(request)
