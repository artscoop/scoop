# coding: utf-8
import hashlib
import logging
import urllib

from django import template
from django.conf import settings
from django.db.models.fields.files import FieldFile
from django.template.defaultfilters import urlencode
from django.template.loader import render_to_string
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer
from scoop.content.models import Animation, Picture
from scoop.content.util.picture import get_context_picture_url

register = template.Library()
logger = logging.getLogger(__name__)


def string_to_dict(options):
    """
    Convertir une chaîne d'options k=v en dictionnaire

    :param options: chaîne du type 'a1 a2=v2 a3=v3'
    """
    output = dict()
    tokens = options.split()
    for token in tokens:
        if token.strip():
            if '=' in token:
                arg, value = token.split('=')
                output[arg] = value
            else:
                output[token] = True
    return output


@register.simple_tag(takes_context=True, name='image')
def display_image(context, image=None, **kwargs):
    """
    Afficher une miniature avec ou sans lien

    :param image: URL d'image ou objet du modèle content.Picture
    :param kwargs: dictionnaire des paramètres
        - alias : alias de configuration de miniature
        - options : chaîne décrivant les options easy-thumbails de génération
        - image_class : classe CSS de l'élément img
        - image_rel : attribut rel de l'élément img
        - link : doit-on afficher un lien autour de l'image ?
        - link_title : attribut title de l'élément a
        - link_class : classe CSS de l'élément a
        - link_id : ID de l'élément a
        - link_rel : attribut rel de l'élément a
        - link_target : URL ou objet avec une méthode get_absolute_url
        - image_title : attribut title de l'élément img
        - image_alt : attribut alt de l'élément img
    """
    request = context.get('request')
    display = Picture.get_display(request, image, **kwargs)
    return render_to_string('content/display/picture/templatetags/image.html', display)


@register.filter
def full_url(picture, request):
    """ Renvoyer l'URL complète de l'image """
    return request.build_absolute_uri(picture.image.url)


@register.filter
def lookup_url(picture, request):
    """ Renvoyer l'URL de recherche d'images similaires Google """
    return "http://www.google.com/searchbyimage?image_url={url}".format(url=urlencode(urlencode(full_url(picture, request))))


@register.filter
def is_picture(item):
    """ Renvoyer si un objet est une image """
    return isinstance(item, Picture)


@register.filter
def picture_animations(picture, width=160):
    """ Renvoyer le code HTML des animations de l'image """
    return Animation.objects.get_html_for_picture(picture, width)


@register.simple_tag(name="context_image")
def context_image_url(name, ext=None, *args):
    """
    Renvoyer une URL d'image située dans settings.USER_DEFAULT_PICTURE_PATH
    et paramétrée via une liste d'arguments, de sorte que le fichier soit
    nommé context-<name>-arg0-arg1.<ext|jpg>
    """
    return get_context_picture_url(name, ext=ext, *args)


@register.assignment_tag
def all_pictures(request=None):
    """ Renvoyer toutes les images du site accessibles à l'utilisateur courant """
    return Picture.objects.by_request(request).select_related().all()


@register.filter(name="gravatar")
def gravatar_url(value, size=r'160x160'):
    """ Renvoyer l'URL du gravatar pour une adresse donnée """
    gravatar = "http://www.gravatar.com/avatar/{}?{}".format(hashlib.md5(value.lower()).hexdigest(), urllib.urlencode({'s': size}))
    return gravatar
