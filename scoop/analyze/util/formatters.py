# coding: utf-8
from django.template.defaultfilters import striptags

from scoop.core.templatetags.text_tags import truncate_longwords, truncate_stuckkey
from scoop.core.util.data.textutil import one_line


def format_base(document):
    """
    Renvoie une version modifiée du document pour la mise en classification

    Ex. Met le contenu en minuscules, retire le HTML etc.
    :param document: Texte du document
    """
    document = striptags(document).lower()
    document = one_line(document)
    document = truncate_longwords(truncate_stuckkey(document))
    return document
