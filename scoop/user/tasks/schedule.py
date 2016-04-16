# coding: utf-8
import logging

from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from scoop.user.access.models import UserIP
from scoop.user.models import User


logger = logging.getLogger(__name__)


@periodic_task(run_every=timedelta(minutes=5), ignore_result=True)
@transaction.atomic()
def clean_online_list():
    """ Mettre à jour la liste des utilisateurs en ligne """
    User._clean_online_list()
    User.get_online_users().update(last_online=timezone.now())
    return True


@periodic_task(run_every=crontab(hour=0, minute=0))
def rebuild_users():
    """ Assurer l'intégrité des liens de clés étrangères """
    User = get_user_model()
    # Assigner des villes si absentes à celles des IP
    if apps.is_installed('scoop.location'):
        users = User.objects.filter(profile__city__isnull=True)
        for user in users:
            city = UserIP.objects.get_city_for(user)
            if city is not None:
                user.profile.city = city
                user.profile.save()
    return True


@periodic_task(run_every=timedelta(hours=12), ignore_result=True)
def update_ages():
    """ Mettre à jour l'âge des profils dont c'est l'anniversaire """
    today = timezone.now()
    today_id = today.month * 100 + today.day
    people = User.objects.filter(profile__birthday=today_id, profile__updated__lt=today.date())
    for person in people:
        person.profile.save(update_fields=['age', 'updated'])
