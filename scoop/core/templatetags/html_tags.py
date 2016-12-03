# coding: utf-8
import re

from bs4 import BeautifulSoup

import bleach
from django import template
from django.conf import settings
from django.utils.html import escape, urlize
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from scoop.core.util.stream.urlutil import get_domain

register = template.Library()


# Nettoyage du code HTML
@register.filter(name="sanitize")
def sanitize(value):
    """ Assainir le contenu HTML """
    tags = ['p', 'i', 'strong', 'small', 'b', '', 'a', 'em', 'pre', 'blockquote', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'sub', 'sup', 'div', 'span']
    return bleach.clean(value, tags=tags)


@register.filter(name="tags_keep")
def tags_keep(value, valid=None):
    """
    Conserver uniquement certains tags du markup HTML
    Tags autorisés : p i b u a strong pre h1 h2 h3 br
    Attributs autorisés : href src rel target class id
    """
    valid_tags, valid_attrs = (valid or 'p i strong b u a h1 h2 h3 pre br').split(), 'href src rel target class id'.split()
    return bleach.clean(value, tags=valid_tags, attributes=valid_attrs)


# Conversion texte vers HTML
@register.filter(name="linebreaks_to_html")
def linebreaks_convert(value):
    """ Transformer les sauts de ligne en sauts HTML """
    output = re.sub(r"(\n)+", "<br>", value)
    output = re.sub(r"(<br\s*/?>\s*){2,20}", "<br>", output, flags=re.I)
    output = re.sub(r"^<br>", "", output, flags=re.I)  # supprimer au début de ligne
    return mark_safe(output)


@register.filter
def truncate_longwords_html(value, length=27):
    """
    Couper les mots beaucoup trop longs, de type « soupe de touches »
    Permet de combattre les pratiques de sabotage des mises en pages
    ex. abcdefghijklmnopqrstuvwxyzabc devient abcdefghijklmnopqrstuvwxyza bc
    """
    re.DEBUG = settings.DEBUG
    soup = BeautifulSoup(value, 'lxml')
    texts = soup.findAll(text=True)

    # Sous fonction : récupère un match et le coupe
    def cut_match(match):
        portion = list(match.group())
        portion.insert(length - 1, ' ')
        return "".join(portion)

    # Supprimer toutes les séquences de la même lettre par cut_match
    pattern = r"\S{{{0}}}".format(int(length))
    for text in texts:
        new_text = re.sub(pattern, cut_match, text)
        text.replaceWith(new_text)
    return mark_safe(soup.renderContents().decode('utf8'))


# Liens
@register.filter(name="linkify")
def linkify(value):
    """ Renvoyer un lien HTML vers un objet """
    if hasattr(value, 'get_absolute_url'):
        return mark_safe("<a href='{domain}{url}'>{name}</a>".format(domain=get_domain(), url=getattr(value, 'get_absolute_url', lambda: "#")(),
                                                                     name=escape(value) or _("None"))) if value else ""
    return escape(value)


@register.filter
def html_urlize(value, autoescape=None):
    """ Transformer les textes contenant des URLs en liens, dans un texte HTML """
    IGNORED_TAGS = {'a', 'code', 'pre'}
    soup = BeautifulSoup(value, 'lxml')
    texts = soup.findAll(name=lambda tag: tag not in IGNORED_TAGS, text=True)
    # Supprimer toutes les séquences de la même lettre par cut_match
    for text in texts:
        new_text = urlize(text)
        text.replaceWith(BeautifulSoup(new_text, 'lxml'))
    # Parcourir tous les liens et ajouter rel = nofollow
    soup = BeautifulSoup(soup.renderContents(), 'lxml')
    links = soup.findAll('a', limit=2)
    for link in links:
        if 'rel' in link:
            del link['rel']
        link.attrs['rel'] = 'nofollow'
    return mark_safe(str(soup))


@register.filter(name="lightboxify")
def lightboxify(value):
    """ Créer un lien lightbox vers un objet """
    return mark_safe(
        "<a href='%(url)s' title='%(name)s' rel='iframe'>%(name)s</a>" % {'url': value.get_absolute_url() if hasattr(value, 'get_absolute_url') else "#",
                                                                          'name': escape(value) or _("None")}) if value else ""


# Listes
@register.filter(name="ul")
def ul(value):
    """
    Renvoyer une liste d'objets en liste non ordonnée de liens

    :type value: list | tuple | set
    """
    output = ["<ul>", "".join(["<li>%s</li>" % linkify(item) for item in value]), "</ul>"]
    return mark_safe("".join(output))


@register.filter(name="ol")
def ol(value):
    """ Renvoyer une liste d'objets en liste ordonnée de liens """
    output = ["<ol>", "".join(["<li>%s</li>" % linkify(item) for item in value]), "</ol>"]
    return mark_safe("".join(output))


@register.filter(name="list")
def list_enumerate(valueset, as_links=True):
    """ Renvoyer un texte d'énumération d'objets """
    output = []
    length = len(valueset)
    finaljoin = _(" and ")
    for idx, item in enumerate(valueset):
        if 0 < idx < length - 1:
            output.append(", ")
        if idx == length - 1 > 0:
            output.append(finaljoin)
        output.append(linkify(item) if as_links else str(item))
    return mark_safe("".join(output))


# Mise en forme simple
@register.filter(name="strong")
def bold(value):
    """ Renvoyer le HTML en gras """
    return mark_safe("<strong>%(value)s</strong>" % {'value': value})
