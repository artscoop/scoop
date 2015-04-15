# coding: utf-8
from __future__ import absolute_import

from django.template.defaultfilters import striptags, truncatewords_html

from scoop.core.templatetags.html_tags import linebreaks_convert, tags_keep, truncate_longwords_html


def format_message(text, limit=1024, strip_tags=False):
    """
    Opérations sur le texte des messages privés
    1. Retirer tous les tags ou n'en garder que les principaux
    2. Transformer tous les sauts de lignes en balises <br>
    3. Couper en deux les mots trop longs
    4. Limiter le texte à un nombre de mots proche de la limite en caractères
    """
    body = striptags(text) if strip_tags is True else tags_keep(text, "strong b p u i h2 h3 pre br")
    body = linebreaks_convert(body)
    body = truncate_longwords_html(body)
    body = truncatewords_html(body, limit / 5)
    return body
