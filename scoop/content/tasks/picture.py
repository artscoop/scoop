# coding: utf-8
from celery import task
from easy_thumbnails.files import generate_all_aliases


@task(name='content.generate_aliases', ignore_result=False)
def generate_aliases(model, pk, field):
    """ Générer les miniatures de l'image """
    try:
        instance = model.objects.get(pk=pk)
        fieldfile = getattr(instance, field)
        generate_all_aliases(fieldfile, include_global=True)
    except model.DoesNotExist:
        pass
