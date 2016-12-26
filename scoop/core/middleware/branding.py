# coding: utf-8
from scoop.core.templatetags.text_tags import site_brand
from scoop.core.util.django.middleware import MiddlewareBase


class BrandingMiddleware(MiddlewareBase):
    """ Middleware remplaçant tous les marqueurs de branding par la marque du site """

    # Constantes
    BLACKLISTED_PATHS = ('/admin', '/manage/')

    # Middleware
    def __call__(self, request):
        """ Traiter le contenu HTML de la réponse """
        response = self.get_response(request)
        if not [True for path in BrandingMiddleware.BLACKLISTED_PATHS if path in request.path]:
            if request.method == 'GET' and response.status_code == 200 and 'text' in response['Content-Type']:
                response.content = site_brand(response.content.decode('utf-8'))
        return response
