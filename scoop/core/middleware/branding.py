# coding: utf-8
from scoop.core.templatetags.text_tags import site_brand


class BrandingMiddleware(object):
    """ Middleware remplaçant tous les marqueurs de branding par la marque du site """

    def process_response(self, request, response):
        """ Traiter le contenu HTML de la réponse """
        if request.method == 'GET' and response.status_code == 200 and 'text' in response['Content-Type']:
            response.content = site_brand(response.content.decode('utf-8'))
        return response
