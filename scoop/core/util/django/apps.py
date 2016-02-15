# coding: utf-8
from django.apps.registry import apps


def is_installed(app_name, retval=None):
    """
    Décorateur exécutant la fonction si une ou plusieurs applications sont installées

    :param app_name: Nom de l'application Django (pas le app_label)
    :type app_name: str
    """

    def wrapper(func):
        def wrapped(*args, **kwargs):
            app_names = app_name if type(app_name) == list else [app_name]
            if all(apps.is_installed(app_name) for app_name in app_names):
                return func(*args, **kwargs)
            return retval

        return wrapped

    return wrapper
