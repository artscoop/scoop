# coding: utf-8
from celery import task


@task(ignore_result=True)
def recalculate_topic_count(forum):
    """ Recalculer le nombre de sujets d'un forum """
    return forum.get_topic_count()
