# coding: utf-8
import re
from re import split

from django import template
from django.core.urlresolvers import reverse
from django.template import Node, Variable, resolve_variable

register = template.Library()


@register.simple_tag
def active(request, pattern, value="active"):
    """ Renvoyer un texte si le chmin correspond à un pattern """
    return value if re.search(pattern, request.path) else ""


@register.simple_tag
def active_named(request, name, value="active"):
    """ Renvoyer un texte si le chemin correspond à une URL nommée """
    url = "^{}$".format(reverse(name))
    return value if re.search(url, request.path) else ""


@register.filter
def url_named(request, name):
    """ Renvoyer si le chemin correspond à une URL nommée """
    return request.resolver_match.url_name == name


@register.filter
def url_name(request):
    """ Renvoyer le nom d'URL de la page """
    try:
        return request.resolver_match.url_name
    except:
        return ""


class AddGetParameter(Node):
    """ Nœud de template qui ajoute un paramètre GET à l'URL """

    def __init__(self, values):
        """ Initialiser le nœud """
        self.values = values

    def render(self, context):
        """ Effectuer le rendu du nœud """
        req = resolve_variable('request', context)
        params = req.GET.copy()
        for key, value in self.values.items():
            params[key] = Variable(value).resolve(context)
        return '?%s' % params.urlencode()


@register.tag
def add_get_parameter(parser, token):
    """ Ajouter un paramètre GET à l'URL """
    contents = split(r'\s+', token.contents, 2)[1]
    pairs = split(r',', contents)
    values = {}
    for pair in pairs:
        s = split(r'=', pair, 2)
        values[s[0]] = s[1]
    return AddGetParameter(values)
