# coding: utf-8

from django import template

from scoop.menus.util import get_menu


register = template.Library()


@register.simple_tag(name='menu', takes_context=True)
def render_menu(context, alias='nav', item=None):
    """ Afficher le menu correspondant à l'alias passé """
    menu = item
    if menu is None:
        menu = get_menu(alias) if isinstance(alias, str) else alias
    print(menu)
    request = context['request']
    return menu.render(request=request)
