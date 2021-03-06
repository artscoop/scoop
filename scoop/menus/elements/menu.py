# coding: utf-8
from django.template.loader import render_to_string

from .item import Item


class Menu(object):
    """
    Menu complet (racine contenant les Items)

    Un menu n'a pas de libellé, ce n'est qu'un conteneur
    """

    name = "Menu container"
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
        return "Menu {name} ({count} children)".format(name=self.name, count=len(self.children))

    # Setter
    def add_children(self, *items):
        """
        Ajouter un sous-menu à l'élément

        Perd son utilité si get_children est modifié et n'utilise
        pas Menu.children.
        """
        if self.children is None:
            self.children = []
        for item in items:
            if isinstance(item, Item):
                self.children.append(item)

    # Getter
    def get_children(self, request=None):
        """
        Renvoyer les éléments enfants du menu

        Peut être overridé pour renvoyer une liste d'éléments enfants
        dynamique.

        :param request: requête HTTP
        """
        return self.children or tuple()

    # Rendu
    def render(self, request, style=None):
        """ Rendre le menu """
        outputs = [child.render(request, style=self.style) for child in self.get_children(request)]
        data = {'children': outputs, 'menu': self}
        return render_to_string('menus/menu-menu-{style}.html'.format(style=self.style or 'nav'), data, request)
