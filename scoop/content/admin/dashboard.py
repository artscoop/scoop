# coding: utf-8
from admin_tools.dashboard.modules import DashboardModule
from django.template.loader import render_to_string

from scoop.content.models import Content, Picture


class BlogRollModule(DashboardModule):
    """ Dashboard des billets de blog """
    pre_content = ""
    title = "Blogs"

    def init_with_context(self, context):
        """ Initialiser le contenu du dashboard """
        blogs = Content.objects.by_category('blog').order_by('-id')[0:5]
        output = render_to_string("content/dashboard/blogs.html", {'blogs': blogs}, context_instance=context)
        self.pre_content = output


class PictureModule(DashboardModule):
    """ Dashboard des dernières images """

    pre_content = ""
    title = "Pictures"

    def init_with_context(self, context):
        """ Initialiser le contenu du dashboard """
        pictures = Picture.objects.all().order_by('-id')
        stats = {'count': Picture.objects.count()}
        output = render_to_string("content/dashboard/pictures.html", {'pictures': pictures, 'stats': stats}, context_instance=context)
        self.pre_content = output
