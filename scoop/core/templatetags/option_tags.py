# coding: utf-8
from __future__ import absolute_import

from django import template

register = template.Library()


@register.simple_tag(name="option")
def option_format(option, mode="label", name=None):
    """ Renvoyer une option formatée en HTML """
    if hasattr(option, 'html'):
        return option.html(mode=mode, name=name)
    return ""
