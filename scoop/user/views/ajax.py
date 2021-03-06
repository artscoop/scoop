# coding: utf-8
from django.contrib.auth.decorators import user_passes_test
from django.http.response import HttpResponse
from django.template.context import RequestContext
from scoop.core.util.django.views import require_ajax
from scoop.user.admin.dashboard import OnlineModule
from scoop.user.util.auth import is_staff


@require_ajax
@user_passes_test(is_staff)
def view_online_dashboard(request):
    """ Afficher le dashboard utilisateurs pour admin-tools """
    dashboard = OnlineModule()
    dashboard.init_with_context(RequestContext(request))
    return HttpResponse(dashboard.pre_content)
