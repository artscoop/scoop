# coding: utf-8


class MiddlewareBase(object):
    """ Mixin pour écrire des middleware Classe compatibles avec Django 1.10+ """

    # Base
    def __init__(self, get_response):
        self.get_response = get_response
