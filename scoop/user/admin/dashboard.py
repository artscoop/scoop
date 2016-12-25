# coding: utf-8
from admin_tools.dashboard.modules import DashboardModule
from django.template.loader import render_to_string


class OnlineModule(DashboardModule):
    """ Dashboard admin-tools des membres en ligne """
    pre_content = ""
    title = "Users"

    def init_with_context(self, context):
        """ Initialiser le contenu du dashboard """
        from scoop.user.models import User
        # Informations
        users = User.get_online_users()
        count = User.get_online_count()
        total = User.objects.active().count()
        category = {'men': User.objects.active().filter(profile__gender=0).count(), 'women': User.objects.active().filter(profile__gender=1).count()}
        output = render_to_string("user/dashboard/online.html", {'users': users, 'count': count, 'total': total, 'numbers': category}, context['request'])
        self.pre_content = output

    def is_empty(self):
        """ Renvoyer si le dashboard est vide """
        return False
