# coding: utf-8
from django.http import HttpResponse

from scoop.core.util.django.middleware import MiddlewareBase
from scoop.editorial.models.page import Page


class EditorialFallbackMiddleware(MiddlewareBase):
    """ Middleware d'accès aux pages éditoriales """

    def __call__(self, request):
        """ Traiter la réponse """
        # En cas autre que 404, renvoyer la réponse inchangée
        response = self.get_response(request)
        if response.status_code in {404, 410}:
            page = Page.objects.get_page(request)
            if page is not None and page.is_visible(request):
                return HttpResponse(page.render())
        return response
