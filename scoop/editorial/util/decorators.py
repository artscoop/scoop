# coding: utf-8


EDITORIAL_VIEW_ATTRIBUTE = '_editorial_view'


def editorial_view(**kwargs):
    """ Définir des attributs à une méthode ou fonction """

    def decorator(func):
        setattr(func, EDITORIAL_VIEW_ATTRIBUTE, True)
        return func

    return decorator
