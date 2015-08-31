# coding: utf-8
from __future__ import absolute_import

from celery import task
from django.conf import settings


@task(name='core.add_record', ignore_result=True)
def record_action_async(actor, action, target=None, content=None):
    """ Enregistrer une action """
    from scoop.core.models.recorder import Record, ActionType
    from scoop.user.models import User
    # N'enregistrer des actions que si les paramètres l'autorisent
    if getattr(settings, 'CORE_ACTION_RECORD', True):
        # L'action peut être une instance d'Action ou un codename d'action
        if isinstance(action, str):
            action = ActionType.objects.get_by_name(action)
        # Créer l'enregistrement si l'action existe dans le système
        if action is not None:
            entry = Record(user=actor or User.objects.get_anonymous(), type=action)
            entry.target_object = target
            entry.container_object = content
            entry.save()
