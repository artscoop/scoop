# coding: utf-8
from celery import task


@task()
def populate_similar(content, *args, **kwargs):
    """ Définir les contenus similaires à un document """
    result = content._populate_similar(*args, **kwargs)
    content.save(started=True)
    return result
