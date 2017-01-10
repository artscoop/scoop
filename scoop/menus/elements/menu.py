# coding: utf-8
from django.utils.safestring import mark_safe

from .item import Item


class Menu(object):
    """ Menu complet (racine contenant les Items) """

    children = None
    style = 'nav'

    # Initialiser
    def __init__(self, *args, **kwargs):
        if args:
            self.add_children(*args)
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation de l'objet """
        return "Menu {name} ({count} enfants)".format(name=self.__class__.__name__, count=len(self.children))

    # Setter
    def add_children(self, *items):
        """ Ajouter un sousèmenu à l'élément """
        if self.children is None:
            self.children = []
        for item in items:
            if isinstance(item, Item):
                self.children.append(item)

    # Rendu
    def render(self, request):
        """ Rendre le menu """
        outputs = [child.render(request, style=self.style) for child in self.children]
        return mark_safe("".join(outputs))
