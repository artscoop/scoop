# coding: utf-8
from functools import lru_cache

from django import template
from django.db.models import Q
from django.template.loader import render_to_string
from scoop.editorial.models.excerpt import Excerpt
from scoop.editorial.models.page import Page

register = template.Library()


@register.simple_tag
def url_page(value):
    """ Renvoyer l'URL d'une page éditoriale via nom ou uuid """
    pages = Page.objects.filter(Q(uuid=value) | Q(name__iexact=value))
    if pages.exists():
        return pages.first().path
    return None


@register.simple_tag
# @lru_cache(256)
def excerpt(name, request=None, mode=None):
    """ Renvoyer le contenu d'un extrait """
    try:
        item = Excerpt.objects.get(name=name)
        template_path = 'editorial/display/excerpt/excerpt-{mode}.html'.format(mode=mode or 'default')
        data = {'excerpt': item}
        if request is not None:
            data['request'] = request
            data['user'] = request.user
        output = render_to_string(template_path, data)
        return output
    except Excerpt.DoesNotExist:
        return "<span class='excerpt-na'></span>"
