# coding: utf-8
from BeautifulSoup import BeautifulSoup
from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from scoop.content.models.advertisement import Advertisement

register = template.Library()


@register.filter(name="insert_ad")
def ads(value, group=""):
    """ Intégrer une annonce publicitaire à un contenu """
    soup = BeautifulSoup(value)
    paragraphs = soup.findAll('p', recursive=False)
    # N'insérer le bloc que si le contenu présente au moins 2 paragraphes
    if len(paragraphs) > 1:
        content = '<p class="content-ads">%(block)s</p>' % {'block': show_ad(group=group)}
        paragraphs[0].append(content)
    # Renvoyer le code HTML modifié
    return soup.renderContents()


@register.simple_tag(name="advertisement")
def show_ad(**options):
    """ Afficher une annonce """
    args = {'group': None, 'name': None, 'size': None}
    for option, value in options.items():
        args[option] = value
    if args['group'] is None and args['name'] is None and args['size'] is None:
        return _(u"[group/name missing]")
    if args['group'] is not None:
        advert = Advertisement.objects.random(args['group'])
    elif args['name'] is not None:
        advert = Advertisement.objects.get_by_name(args['name'])
    elif args['size'] is not None:
        width, height = [int(item) for item in args['size'].split('x')]
        advert = Advertisement.objects.random_by_size(width, height)
    if advert is not None:
        return render_to_string("content/display/advertisement.html", {'ad': advert.render()})
    if settings.DEBUG:
        return _(u"advertisement missing")
    return ""
