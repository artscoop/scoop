# coding: utf-8
from __future__ import absolute_import

from functools import wraps

from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.template.loader import render_to_string
from django.template.loader_tags import BlockNode, ExtendsNode


def render_to_code(request, name, dictionary, code=200):
    """ Renvoyer un HTTPResponse avec le contenu d'un template et le code HTTP désiré """
    response = render_to_response(name, dictionary, context_instance=RequestContext(request))
    response.status_code = code
    return response


def _get_template(template):
    if isinstance(template, (tuple, list)):
        return loader.select_template(template)
    return loader.get_template(template)


class BlockNotFound(Exception):
    """The requested block did not exist."""
    pass


def render_template_block(template, block, context):
    """ Effectuer le rendu d'un bloc unique d'un template """
    template.render(context)
    return _render_template_block_nodelist(template.template.nodelist, block, context)


def _render_template_block_nodelist(nodelist, block, context):
    """ Parcourir le template à la recherche d'un noeud de type block """
    for node in nodelist:
        if isinstance(node, BlockNode) and node.name == block:
            return node.render(context)
        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if hasattr(node, key):
                try:
                    rendered = _render_template_block_nodelist(getattr(node, key), block, context)
                except:
                    pass
                else:
                    return rendered
    for node in nodelist:
        if isinstance(node, ExtendsNode):
            try:
                resolve_parent = node.parent_name.resolve(context)
                rendered = render_template_block(loader.get_template(resolve_parent), block, context)
            except BlockNotFound:
                pass
            else:
                return rendered
    raise BlockNotFound


def render_block_to_string(template_name, block, extra_context=None, context_instance=None):
    """
    Rendre un seul block de template dans une chaîne
    :param extra_context: contexte supplémentaire à passer
    :param block: nom du bloc à rendre
    :param context_instance: objet Context ou RequestContext
    """
    extra_context = extra_context or {}
    template = _get_template(template_name)
    if context_instance:
        context_instance.update(extra_context)
    else:
        context_instance = Context(extra_context)
    return render_template_block(template, block, context_instance)


def render_block_to_response(request, template, block, extra_context=None, content_type=None, **kwargs):
    """
    Rendre un seul block de template dans un objet HTTPResponse
    :param request: objet Request
    :param template: nom du template à parcourir
    :param block: nom du bloc à rendre
    :param extra_context: contexte supplémentaire à passer
    :param content_type: type MIME de la sortie, ex.:text/html
    """
    if extra_context is None:
        extra_context = {}
    dictionary = {'params': kwargs}
    for key, value in extra_context.items():
        if callable(value):
            dictionary[key] = value()
        else:
            dictionary[key] = value
    c = RequestContext(request, dictionary)
    template = _get_template(template)
    template.render(c)
    return HttpResponse(render_template_block(template, block, c), content_type=content_type or 'text/html')


def render_to(template=None, content_type=None, headers=None, status_code=200, string=False):
    """
    Décorateur de rendu d'un template.
    La fonction en argument peut renvoyer un objet HTTPResponse ou un dictionnaire
    :param template: nom du template à rendre
    :param content_type: type MIME de la sortie
    :param headers: dictionnaire d'en-têtes de réponse
    :param status_code: code de retour HTTP
    :param string: indique si le rendu se fait dans une chaîne plutôt que HTTPResponse
    :returns un objet HTTPResponse, une chaîne ou l'objet retourné par la fonction décorée
    """

    def renderer(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, (dict, type(None))):
                return output
            tmpl = output.pop('set.template', template)
            head = output.pop('set.headers', headers)
            code = output.pop('set.status_code', status_code)
            if string is False:
                response = render_to_response(tmpl, output, context_instance=RequestContext(request), content_type=content_type or 'text/html')
                response.status_code = code
                if type(head) == dict:
                    for key, value in head.items():
                        response[key] = value
                return response
            else:
                rendered = render_to_string(tmpl, output, context_instance=RequestContext(request))
                return rendered

        return wrapper

    return renderer


def do_render(data, request, template=None, content_type=None, headers=None, status_code=200, string=False):
    """
    Rendre un template.
    :param data: contexte supplémentaire
    :param request: objet HTTPRequest
    :param template: nom du template à rendre
    :param content_type: type MIME de la sortie
    :param headers: dictionnaire d'en-têtes de réponse
    :param status_code: code de retour HTTP
    :param string: indique si le rendu se fait dans une chaîne plutôt que HTTPResponse
    """
    if not isinstance(data, dict):
        return data
    tmpl = data.pop('set.template', template)
    head = data.pop('set.headers', headers)
    code = data.pop('set.status_code', status_code)
    if string is False:
        response = render_to_response(tmpl, data, context_instance=RequestContext(request), content_type=content_type)
        response.status_code = code
        if type(head) == dict:
            for key, value in head.items():
                response[key] = value
        return response
    else:
        rendered = render_to_string(tmpl, data, context_instance=RequestContext(request))
        return rendered
