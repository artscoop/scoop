# coding: utf-8
from .item import Item


class Menu(object):
    """ Menu complet (racine contenant les Items) """

    children = None

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
        outputs = [child.render(request) for child in self.children]
        return "".join(outputs)
