# coding: utf-8


class Dictionary(dict):
    """
    Dictionnaire auquel on peut assigner des attributs/métadonnées

    >>> d = Dictionary()
    >>> d.attribute = None
    >>> assert d.attribute is None
    """
    pass


class List(list):
    """
    Liste à laquelle on peut assigner des attributs/métadonnées

    >>> d = List()
    >>> d.attribute = None
    >>> assert d.attribute is None
    """
    pass
