# coding: utf-8
from __future__ import absolute_import

from django.http import HttpResponse

from scoop.editorial.models.page import Page


class EditorialFallbackMiddleware(object):
    """ Middleware d'accès aux pages éditoriales """

    def process_response(self, request, response):
        """ Traiter la réponse """
        # En cas autre que 404, renvoyer la réponse inchangée
        if response.status_code in {404, 410}:
            page = Page.objects.get_page(request)
            if page is not None and page.is_visible(request):
                return HttpResponse(page.render())
        return response
