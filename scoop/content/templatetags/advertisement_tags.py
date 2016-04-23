# coding: utf-8
from bs4 import BeautifulSoup

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
    args.update(options)
    advert = Advertisement.objects.select_ad(**args)
    if advert is not None:
        return render_to_string("content/display/advertisement/html/default.html", {'ad': advert.render()})
    if settings.DEBUG:
        return _("advertisement missing")
    return ""
