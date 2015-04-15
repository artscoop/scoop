# coding: utf-8
from __future__ import absolute_import

from django import template

from scoop.content.models.content import Content
from scoop.core.util.data.textutil import clean_html

register = template.Library()


@register.filter
def is_editable(content, author):
    """ Renvoyer si le contenu est modifiable par un utilisateur """
    return content.is_editable(author)


@register.assignment_tag
def month_content(month, *args, **kwargs):
    """ Renvoyer les contenus pour un mois """
    criteria = {'category__short_name': kwargs['category']} if kwargs.get('category', None) else {}
    contents = Content.objects.by_month(month, **criteria)
    return contents


@register.assignment_tag
def content_month_list():
    """ Renvoyer la liste des mois de publication de contenu """
    return Content.objects.get_months()


@register.filter
def content(user, category_name=None):
    """ Renvoyer les contenus de l'auteur et d'une certaine catégorie """
    return Content.objects.by_author(user) if not category_name else Content.objects.by_category(category_name, authors=user)


@register.assignment_tag
def get_content(category_name=None, randomize=True):
    """ Renvoyer un contenu au hasard dans une catégorie """
    entries = Content.objects.visible()
    if isinstance(category_name, basestring):
        entries = entries.by_category(category_name)
    if randomize is True:
        entries = entries.order_by('?')
    return entries[0] if entries.exists() else Content.objects.none()


@register.filter
def similarity(content, other_content):
    """ Renvoyer l'indice de similarité entre 2 contenus """
    if isinstance(content, Content) and isinstance(other_content, Content):
        similarity = content.get_similarity(other_content)
        return similarity
    else:
        return None


@register.filter(name='clean_html')
def clean_html_(text):
    """ Renvoyer un contenu HTML nettoyé """
    return clean_html(text)
