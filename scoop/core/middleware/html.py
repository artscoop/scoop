# coding: utf-8
import re

from bs4 import BeautifulSoup as bs

from html5print.html5print import HTMLBeautifier
from scoop.core.util.data.textutil import replace_dict
from scoop.core.util.django.middleware import MiddlewareBase


class FormatHTMLMiddleware(MiddlewareBase):
    """ Middleware formatant la sortie HTML """

    # Constantes
    UNCHANGED_TAGS = ['textarea', 'pre', 'script', 'button']

    def __call__(self, request):
        """ Traiter le contenu HTML de la réponse """
        response = self.get_response(request)
        if 'text/html' in response['Content-Type']:
            getattr(response, 'render', int)()
            output = replace_dict(response.content, {'{': '{{', '}': '}}'})
            soup = bs(output)
            unformatted_tag_list = []
            for i, tag in enumerate(soup.find_all(self.UNCHANGED_TAGS)):
                unformatted_tag_list.append(tag)
                tag.replace_with('{' + 'unformatted_tag_list[{0}]'.format(i) + '}')
            output = soup.prettify(formatter="minimal").format(unformatted_tag_list=unformatted_tag_list)
            r = re.compile(r'^(\s*)', re.MULTILINE)
            output = r.sub(r'\1' * 4, output)
            response.content = replace_dict(output, {'{{': '{', '}}': '}'})
        return response


class FormatHTML5Middleware(MiddlewareBase):
    """ Middleware formatant le contenu HTML de la page """

    def __call__(self, request):
        """ Traiter le contenu HTML de la réponse """
        response = self.get_response(request)
        if 'text/html' in response['Content-Type']:
            getattr(response, 'render', int)()
            response.content = HTMLBeautifier.beautify(response.content)
        return response


class SpacelessMiddleware(MiddlewareBase):
    """ Middleware formatant la sortie HTML en supprimant tous les espaces possibles """

    # Constantes
    UNCHANGED_TAGS = ['textarea', 'pre', 'button']

    def __call__(self, request):
        """ Traiter le contenu de la réponse """
        response = self.get_response(request)
        if 'text/html' in response['Content-Type']:
            getattr(response, 'render', int)()
            output = replace_dict(response.content, {'{': '{{', '}': '}}'})
            soup = bs(output)
            unformatted_tag_list = []
            for i, tag in enumerate(soup.find_all(self.UNCHANGED_TAGS)):
                unformatted_tag_list.append(tag)
                tag.replace_with('{' + 'unformatted_tag_list[{0}]'.format(i) + '}')
            output = soup.prettify(formatter="minimal")
            r = re.compile(r'\n(\s*)', re.MULTILINE)
            output = r.sub(r' ', output)
            output = output.format(unformatted_tag_list=unformatted_tag_list)
            response.content = replace_dict(output, {'{{': '{', '}}': '}'})
        return response
