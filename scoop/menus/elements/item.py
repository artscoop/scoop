# coding: utf-8
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class Item(object):
    """ Élément de menu """

    identifier = None  # identifiant HTML (+ menu-id- en sortie)
    label = None  # libellé HTML
    target = None  # URL cible (fonction prenant un argument request ou chaîne)
    children = None
    is_child = False  # Renseigné lorsque le menu est ajouté à un autre

    # Initialiseur
    def __init__(self, *args, **kwargs):
        """ Initialiser les propriétés de l'élément de menu """
        super().__init__()
        self.identifier = kwargs.get('identifier', None)
        self.label = kwargs.get('label', None)
        self.target = kwargs.get('target', None)

    # Getter
    def get_absolute_url(self, request):
        """ Renvoyer l'URL cible de l'élément de menu """
        if isinstance(self.target, str):
            return self.target
        elif callable(self.target):
            return self.target(request)
        return "#"  # Renvoyer une URL par défaut

    def is_active(self, request):
        """ Renvoyer si le menu doit être actif pour une requête """
        url = request.path
        return url == self.get_absolute_url()  # Peut aussi s'activer si resolve correspond à un nom d'URL etc.

    def is_visible(self, request):
        """ Renvoyer si le menu doit être rendu pour une requête """
        return True

    def has_children(self):
        """ Renvoyer si des sous-menus existent """
        return self.children is not None

    def get_label(self, request):
        """ Renvoyer le libellé HTML de l'élément """
        return mark_safe(self.label)

    # Setter
    def add_children(self, *items):
        """ Ajouter un sousèmenu à l'élément """
        if self.children is None:
            self.children = []
        for item in items:
            if isinstance(item, Item):
                item.is_child = True
                self.children.append(item)

    # Rendu
    def render(self, request):
        if self.is_visible(request):
            data = {'menu': self, 'active': self.is_active(request), 'url': self.get_absolute_url(request)}
            output = render_to_string("menus/menu-item.html", data, request)
            return output
        return ""  # Ne rien rendre si le menu est invisible
