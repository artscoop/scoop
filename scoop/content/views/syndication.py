# coding: utf-8
from __future__ import absolute_import

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext_lazy as _

from scoop.content.models.content import Content


class BlogContentFeed(Feed):
    """ Flux RSS des contenus blog """
    title = _(u"Recent blog entries published")
    link = "/syndication/blog.xml"
    description = _(u"RSS feed")

    def items(self):
        """ Renvoyer les contenus du flux """
        return Content.objects.by_category(['blog'], published=True).order_by('-time')[:20]

    def item_title(self, item):
        """ Renvoyer le titre d'un contenu """
        return item.title

    def item_description(self, item):
        """ Renvoyer la description d'un contenu """
        return item.get_teaser()
