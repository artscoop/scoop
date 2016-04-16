# coding: utf-8
import logging

from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.utils import timezone


logger = logging.getLogger(__name__)


@periodic_task(run_every=timedelta(days=2, hours=12))
def expire_ip_blocks():
    """ Faire expirer les blocages d'IP """
    from scoop.rogue.models import IPBlock
    return IPBlock.objects.expire()


@periodic_task(run_every=crontab(hour=2, minute=15))
def check_random_users():
    """ Contrôle de routine sur des utilisateurs récents """
    from scoop.user.models import User
    from scoop.rogue.models import IPBlock
    users = User.objects.by_online_range(timezone.now(), timedelta(days=-90))
    # Envoyer le signal « IP bloquée » pour les utilisateurs concernés
    # Voir rogue.listeners.user
    [IPBlock.objects.is_user_blocked(user) for user in users]
