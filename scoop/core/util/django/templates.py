# coding: utf-8
from functools import wraps

from django.http.response import HttpResponse
from django.shortcuts import render
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.template.loader_tags import BlockNode, ExtendsNode

from scoop.core.templatetags.repeat import MacroRoot
from scoop.core.util.stream.request import default_request


def render_to_code(request, template, context, status_code=200):
    """
    Renvoyer un HTTPResponse avec le contenu d'un template et le code HTTP désiré

    :param request: objet HttpRequest
    :param template: nom du template à rendre
    :param context: données de contexte à passer au template
    :param status_code: code de statut HTTP
    :type status_code: int
    :type context: dict
    :type request: HttpRequest
    :type template: str | list | tuple
    :rtype: HttpResponse
    """
    return do_render(context, request, template=template, status_code=status_code)


def _get_template(template):
    if isinstance(template, (tuple, list)):
        return loader.select_template(template)
    return loader.get_template(template)


def render_block_to_string(template_name, block_name, data=None, context=None):
    data = data or {}
    if context:
        context.update(data)
    else:
        context = RequestContext(default_request(), data)

    t = loader.get_template(template_name)
    with context.bind_template(t.template):
        t.template.render(context)

        to_visit = list(t.template.nodelist)  # Copier la liste car la liste de nœuds du template est globale (Django 1.10)
        while to_visit:
            node = to_visit.pop()  # ici on modifie la liste, d'où la nécessité de la copier auparavant
            if isinstance(node, BlockNode) and node.name == block_name:
                return node.render(context)
            elif hasattr(node, 'nodelist'):
                to_visit += node.nodelist
            if isinstance(node, (ExtendsNode, MacroRoot)):
                to_visit += node.get_parent(context).nodelist

    raise RuntimeError("Block not found: {0}".format(block_name))


def render_to(template=None, content_type=None, headers=None, status_code=200, string=False, use_request=True):
    """
    Décorateur de rendu d'un template.

    Prend comme fonction une vue Django (premier paramètre positionnel request)
    Fonctionne avec tous les moteurs de template.

    La fonction en argument peut renvoyer un objet HTTPResponse ou un dictionnaire
    :param template: nom du template à rendre
    :param content_type: type MIME de la sortie
    :param headers: dictionnaire d'en-têtes de réponse
    :param status_code: code de retour HTTP
    :param string: indique si le rendu se fait dans une chaîne plutôt que HTTPResponse
    :param use_request: utiliser un contexte de requête, avec context_processors appliqués
    :type template: str | list | tuple
    :type use_request: bool
    :returns un objet HTTPResponse, une chaîne ou l'objet retourné par la fonction décorée
    """

    def renderer(function):
        """ Décorateur """
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            return do_render(request, template=template, data=output, content_type=content_type, headers=headers, status_code=status_code, string=string,
                             use_request=use_request)

        return wrapper

    return renderer


def do_render(request, template=None, data=None, content_type=None, headers=None, status_code=200, string=False, use_request=True):
    """
    Rendre un template. Fonctionne avec tous les moteurs de template.

    Si use_request est à False, le rendu du template s'effectue sans accès
    aux context_processors et sans accès à l'objet request.
    Ainsi, impossible de récupérer l'utilisateur connecté ainsi que des données comme
    MEDIA_URL et STATIC_URL etc. Cela peut cependant légèrement améliorer
    les performances de rendu du template, vu l'absence d'appel aux context_processors
    (qui peuvent être inutiles avec certains tmeplates)

    :param data: contexte de rendu de la vue.
    :param request: objet HTTPRequest
    :param template: nom du template à rendre
    :param content_type: type MIME de la sortie
    :param headers: dictionnaire d'en-têtes de réponse
    :param status_code: code de retour HTTP
    :param string: indique si le rendu se fait dans une chaîne plutôt que HTTPResponse
    :param use_request: use a request context with processors data added
    :type data: dict | object
    :type template: str | list | tuple
    :type use_request: bool
    """
    if isinstance(data, dict):
        template = data.pop('set.template', template)
        if string is False:
            headers = data.pop('set.headers', headers)
            status_code = data.pop('set.status_code', status_code)
            response = render(request if use_request else None, template, context=data, content_type=content_type, status=status_code)
            if isinstance(headers, dict):
                for key, value in headers.items():
                    response[key] = value
            return response
        else:
            return render_to_string(template, context=data, request=request if use_request else None)
    else:
        return data
