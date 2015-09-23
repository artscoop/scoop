# coding: utf-8
from __future__ import absolute_import

from urllib import parse

from annoying.decorators import render_to
from django.core.validators import URLValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from scoop.content.util.micawber.oembed import bootstrap_oembed
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.generic import NullableGenericModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.user.authorable import AuthorableModel
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.urlutil import get_url_resource


class LinkManager(models.Manager):
    """ Manager des liens """

    # Getter
    def in_group(self, name):
        """ Renvoyer les liens appartenant au groupe désiré """
        return self.filter(group__iexact=name).order_by('weight')

    def get_count_in_group(self, name):
        """ Renvoyer le nombre de liens appartenant à un groupe """
        return self.in_group(name).count()

    def get_with_url(self, text):
        """ Renvoyer le nombre de liens dont l'URL contient un texte """
        return self.filter(url__icontains=text)


class Link(DatetimeModel, NullableGenericModel, AuthorableModel, IconModel, WeightedModel, UUID64Model):
    """ Lien interne ou externe """

    # Constantes
    TYPES = ((0, _("Text")), (1, _("Icon")), (2, _("Icon and text")), (3, _("oEmbed")), (4, _("Flash")))
    # Champs
    group = models.CharField(max_length=16, blank=True, db_index=True, verbose_name=_("Group"), help_text=_("Use the same name to group icons."))
    display = models.SmallIntegerField(choices=TYPES, default=0, db_index=True, help_text=_("Default display mode of this link"), verbose_name=_("Type"))
    url = models.URLField(max_length=1024, unique=True, verbose_name=_("URL"))
    anchor = models.CharField(max_length=192, blank=True, verbose_name=_("Anchor"))
    title = models.CharField(max_length=128, blank=True, verbose_name=_("Title"))
    target = models.CharField(max_length=16, default="_self", blank=True, verbose_name=_("Target"))
    nofollow = models.BooleanField(default=True, verbose_name=_("No-follow"))
    remainder = models.CharField(max_length=64, blank=True, verbose_name=_("HTML Remainder"), help_text=_("HTML code of extra tag attributes"))
    information = models.TextField(blank=True, default="", help_text=_("Internal information for the link"), verbose_name=_("Information"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))
    objects = LinkManager()

    # Getter
    @render_to("content/display/link.html")
    def html(self):
        """ Renvoyer le code HTML du lien """
        return {'link': self}

    @addattr(boolean=True)
    def is_valid(self):
        """ Renvoyer si l'URL est formée correctement """
        parsed = parse.urlparse(self.url)
        try:
            URLValidator(self.url)
        except:
            return False
        return parsed.scheme in ['http', 'https', ''] and parsed.netloc != ''

    @addattr(boolean=True)
    def exists(self):
        """ Renvoyer si l'URL mène à une page valide """
        try:
            if self.is_valid():
                get_url_resource(self.url)
                return True
            return False
        except:
            return False

    def get_oembed(self):
        """ Renvoyer les métadonnées oEmbed """
        from micawber import parsers
        # Renvoyer les données oEmbed
        result = parsers.extract(self.url, bootstrap_oembed)
        return result[1][self.url]

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.url

    # Métadonnées
    class Meta:
        verbose_name = _("link")
        verbose_name_plural = _("links")
        app_label = 'content'
