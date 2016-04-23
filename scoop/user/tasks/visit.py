# coding: utf-8
from celery import task
from scoop.user.models import Visit


@task(rate_limit='50/s', ignore_result=True)
def add_visit(visitor, user):
    """ Ajouter une nouvelle visite d'un profil """
    Visit.objects.create(visitor, user)
