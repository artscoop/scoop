# coding: utf-8
from celery import task


@task(expires=60, rate_limit='2/s')
def populate_similar(content, *args, **kwargs):
    """ Définir les contenus similaires à un document """
    result = content._populate_similar(*args, **kwargs)
    content.save()
    return result
