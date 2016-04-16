# coding: utf-8
from django.dispatch.dispatcher import receiver

from scoop.core.tasks.recorder import record_action_async
from scoop.core.util.model.model import make_lazy_picklable
from scoop.core.util.signals import record


__all__ = ['record_action']


@receiver(record)
def record_action(sender, actor, action, target=None, content=None, **kwargs):
    """ Enregistrer une action dans le log """
    if actor is not None and action is not None:
        actor, target = make_lazy_picklable(actor, target)
        record_action_async.delay(actor, action, target=target, content=content)
