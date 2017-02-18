# coding: utf-8

from django import template

from scoop.menus.util import get_menu


register = template.Library()


@register.simple_tag(name='menu', takes_context=True)
def render_menu(context, alias='nav', style=None):
    """
    Afficher le menu correspondant à l'alias passé

    :argument alias: alias du menu, tel que défini dans les clés de settings.MENU_ALIASES
    :argument context: contexte du template Django
    :argument style: style de l'affichage du menu. Change le suffixe des templates utilisés. 'nav" par défaut
    """
    menu = get_menu(alias) if isinstance(alias, str) else alias
    request = context['request']
    return menu.render(request=request, style=style)


@register.filter(name='menu_label')
def menu_label(item, request):
    """ Renvoyer l'étiquette d'un élément de menu """
    return item.get_label(request)
