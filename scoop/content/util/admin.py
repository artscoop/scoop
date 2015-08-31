# coding: utf-8
from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext

from scoop.core.util.shortcuts import addattr


class PicturedModelAdmin():
    """
    Mixin d'administration permettant d'afficher les images attachées à des
    contenus. Chaque objet ModelAdmin possèdé alors un attribut d'affichage
    des miniatures attachées à un objet de type PicturableModel
    """

    @addattr(allow_tags=True, admin_order_field='pictures', short_description=_("Pictures"))
    def get_picture_set(self, obj):
        """
        Renvoyer les premières miniatures des images attachées à
        l'objet ainsi que le nombre total d'images attachées si nécessaire
        """
        size = (48, 20)
        if hasattr(obj, 'get_pictures') or hasattr(obj, 'pictures'):
            queryset = obj.get_pictures() if hasattr(obj, 'get_pictures') else obj.pictures.all()
            pictures = "".join([picture.get_thumbnail_html(size=size) for picture in queryset[0:2]]) or pgettext('picture', "None")
            if queryset.count() > 2:
                pictures = u'{pictures} <span class="muted">{count}</span>'.format(pictures=pictures, count=queryset.count())
            return pictures
        return _("This model has no field named pictures.")

    @addattr(boolean=True, admin_order_field='pictures', short_description=_("\U0001F58C"))
    def has_picture(self, obj):
        """ Renvoyer si des images sont attachées à l'objet """
        return obj.pictures.all().exists()
