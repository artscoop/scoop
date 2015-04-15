# coding: utf-8
from __future__ import absolute_import

from django import template
from django.db.models import Q
from django.template import Template

from scoop.core.util.stream.request import default_context
from scoop.editorial.models.excerpt import Excerpt
from scoop.editorial.models.page import Page

register = template.Library()


@register.simple_tag
def url_page(request, value=''):
    """ Renvoyer l'URL d'une page éditoriale via nom ou uuid """
    pages = Page.objects.filter(Q(uuid=value) | Q(name__iexact=value))
    if pages.exists():
        return pages.first().path
    return None


@register.simple_tag
def excerpt(name):
    """ Renvoyer le contenu d'un extrait """
    item = Excerpt.objects.get(name=name)
    template = Template(item.html(), name=item.name)
    return template.render(default_context())
