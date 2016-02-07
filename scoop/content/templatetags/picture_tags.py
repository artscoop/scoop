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
    """ Afficher une miniature avec ou sans lien """
    request = context.get('request')
    display = dict()
    # Afficher une image par UUID (remplacer image par uuid)
    if 'uuid' in kwargs:
        image = Picture.objects.get_by_uuid(kwargs.pop('uuid', None), default=image)
    # N'afficher que si l'objet Picture est visible pour l'objet Request
    if image is not None and isinstance(image, (Picture, str, FieldFile)):
        display['alias'] = kwargs.pop('alias')  # alias de vignette
        display['options'] = kwargs.pop('options', "")  # options easy-thumbnails de type bool
        display['image_class'] = kwargs.pop('image_class', "")
        display['image_rel'] = kwargs.pop('image_rel', "")
        display['link_title'] = kwargs.pop('link_title', "")
        display['link_class'] = kwargs.pop('link_class', "")
        display['link_id'] = kwargs.pop('link_id', "")
        display['link_rel'] = kwargs.pop('link_rel', None)
        display['link'] = kwargs.pop('link', True)
        if isinstance(image, Picture) and image.is_visible(request) and image.exists():
            display['image_url'] = image.image
            display['link_target'] = kwargs.pop('link_target', "{}{}".format(settings.MEDIA_URL, image.image))
            display['image_title'] = kwargs.pop('image_title', image.title)
            display['image_alt'] = kwargs.pop('image_alt', image.description)
        elif isinstance(image, (str, FieldFile)):
            display['image_url'] = image
            display['link_target'] = kwargs.pop('link_target', "{}{}".format(settings.MEDIA_URL, image))
            display['image_title'] = kwargs.pop('image_title', "")
            display['image_alt'] = kwargs.pop('image_alt', "")
        else:
            return ""
        # Si link_target est un objet, convertir en URL
        if 'link_target' in display and hasattr(display['link_target'], 'get_absolute_url'):
            display['link_target'] = display['link_target'].get_absolute_url()
        # Convertir l'image en thumbnail si possible
        options = kwargs
        options.update(aliases.get(display['alias']) or {'size': display['alias']})
        options.update(string_to_dict(display['options']))
        display['image_thumbnail'] = get_thumbnailer(display['image_url']).get_thumbnail(options)
        return render_to_string('content/display/picture/templatetags/image.html', display)
    return ""


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
