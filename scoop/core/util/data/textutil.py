# coding: utf-8
import re
from io import StringIO

import bleach
from django.utils.html import strip_tags


def text_to_list_of_lists(value, evaluate=False):
    """
    Renvoyer une liste de listes depuis un texte.
    Chaque élément de la liste de rang 1 est séparé par un retour chariot
    Les éléments des listes de rang 2 sont séparées par deux points (:)
    Attention, evaluate peut représenter une faille de sécurité, n'utiliser
    qu'avec du contenu de confiance.
    :param evaluate: évaluer les valeurs, notamment les nombres
    """
    with StringIO(value) as reader:
        lines = reader.readlines()
        result = [line.split(":") for line in lines if (':' in line and not line.startswith('#'))]
        if evaluate is True:
            for outer, _ in enumerate(result):
                for inner, _ in enumerate(result[outer]):
                    result[outer][inner] = eval(result[outer][inner], {'__builtin__': {}})
    return result


def text_to_dict(value, evaluate=False):
    """
    Renvoyer un dictionnaire depuis un texte
    Chaque couple clé/valeur est sur sa propre ligne, et séparé par deux points (:)
    Attention, evaluate peut représenter une faille de sécurité, n'utiliser
    qu'avec du contenu de confiance.
    :param evaluate: évaluer les valeurs, notamment les nombres
    """
    with StringIO(value) as reader:
        lines = reader.readlines()
        result = dict([line.split(":", 1) for line in lines if (':' in line and not line.startswith('#'))])
        if evaluate is True:
            for key in result.keys():
                result[key] = eval(result[key], {'__builtin__': {}})
    return result


def one_line(value):
    """ Renvoyer le texte, mais sur une seule ligne """
    output = re.sub(r"\r?\n", " ", value).strip()
    return output


def replace_dict(instance, dictionary):
    """
    Renvoyer un texte dont les clés du dictionnaire sont remplacés par les valeurs
    ex. "Les chaussettes de la raine", {'Les': 'Le', 'chaussettes': 'saucisson'}
    renvoie "Le saucisson de la reine"
    """
    result = instance
    for base in dictionary:
        result = result.replace(base, dictionary[base])
    return result


def count_words(text, html=False):
    """ Renvoyer le nombre de mots dans un texte """
    text = strip_tags(text) if html else text
    count = len(re.findall(r'\w+', text))
    return count


def clean_html(text):
    """ Renvoyer un texte HTML filtré à certains tags et attributs """
    allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'p', 'br', 'strong', 'em', 'strike', 'b', 'small', 'code', 'pre', 'blockquote', 'hr', 'dt', 'dd', 'ul', 'li', 'ol', 'span',
                    'center', 'site', 'address', '', 'caption']
    allowed_attr = ['href', 'src', 'class', 'id', 'title', 'alt', 'target', 'rel', 'align', 'style']
    allowed_styles = ['text-align']
    try:
        return bleach.clean(text, allowed_tags, allowed_attr, allowed_styles, strip=True)
    except:
        return text
