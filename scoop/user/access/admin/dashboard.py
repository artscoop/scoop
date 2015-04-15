# coding: utf-8
from admin_tools.dashboard.modules import DashboardModule
from django.template.loader import render_to_string


class IPModule(DashboardModule):
    """ Dashboard admin-tools des adresses IP """
    pre_content = ""
    title = "User IPs"

    def init_with_context(self, context):
        """ Initialiser le contenu du dashboard """
        from scoop.user.access.models import UserIP

        ips = UserIP.objects.all().order_by('-pk')
        output = render_to_string("access/dashboard/ips.html", {'userips': ips}, context_instance=context)
        self.pre_content = output

    def is_empty(self):
        """ Renvoyer si le dashboard est vide """
        return False
