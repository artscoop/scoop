# coding: utf-8
from django.http.response import HttpResponse
from django.template.context import RequestContext
from django.views.generic.base import View


class DashboardView(View):
    """ Mixin de dashboard admin-tools """
    dashboard_class = None  # peut être défini via constructeur

    def get(self, request, *args, **kwargs):
        """ Lors d'une requête GET """
        dashboard = self.dashboard_class()
        dashboard.init_with_context(RequestContext(request))
        response = HttpResponse(dashboard.pre_content)
        response.status_code = 200
        return response
