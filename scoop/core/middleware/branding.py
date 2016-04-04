# coding: utf-8
from scoop.core.templatetags.text_tags import site_brand


class BrandingMiddleware(object):
    """ Middleware remplaçant tous les marqueurs de branding par la marque du site """

    def process_response(self, request, response):
        """ Traiter le contenu HTML de la réponse """
        if 'text' in response['Content-Type']:
            response.content = site_brand(response.content)
        return response