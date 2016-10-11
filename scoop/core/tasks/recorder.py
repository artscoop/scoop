# coding: utf-8
from celery.task import task
from django.conf import settings
from django.db import models
from scoop.core.models.recorder import Record, RecordType
from scoop.user.models import User


@task(name='core.add_record', ignore_result=True, expires=120)
def record_action_async(actor, action, target=None, content=None):
    """ Enregistrer une action """
    if getattr(settings, 'CORE_ACTION_RECORD', True):
        # L'action peut être une instance d'Action ou un codename d'action
        if isinstance(action, str):
            action = RecordType.objects.get_by_name(action)
        # Créer l'enregistrement si l'action existe dans le système
        if action is not None:
            target_object = target if isinstance(target, models.Model) else None
            target_name = str(target) if target is not None else ""
            entry = Record(user=actor or User.objects.get_anonymous(), type=action)
            entry.target_object = target_object
            entry.target_name = target_name
            entry.container_object = content
            entry.save()
            return True
    return False
