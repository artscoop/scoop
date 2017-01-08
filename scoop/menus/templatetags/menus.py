# coding: utf-8

from django import template

from scoop.core.menus.util import get_menu


register = template.Library()


@register.simple_tag(name='menu', takes_context=True)
def render_menu(context, alias='default'):
    """ Afficher le menu correspondant à l'alias passé """
    menu = get_menu(alias) if isinstance(alias, str) else alias
    request = context['request']
    return menu.render(request=request)
