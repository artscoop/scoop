# coding: utf-8
from __future__ import absolute_import

import urlparse

from annoying.decorators import render_to
from django.core.validators import URLValidator
from django.db import models
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
    def get_for_group(self, name):
        """ Renvoyer les liens appartenant au groupe désiré """
        return self.filter(group__iexact=name).order_by('weight')

    def get_count_in_group(self, name):
        """ Renvoyer le nombre de liens appartenant à un groupe """
        return self.get_group(name).count()

    def get_with_url(self, text):
        """ Renvoyer le nombre de liens dont l'URL contient un texte """
        return self.filter(url__icontains=text)


class Link(DatetimeModel, NullableGenericModel, AuthorableModel, IconModel, WeightedModel, UUID64Model):
    """ Lien interne ou externe """

    # Constantes
    TYPES = ((0, _(u"Text")), (1, _(u"Icon")), (2, _(u"Icon and text")), (3, _(u"oEmbed")), (4, _(u"Flash")))
    # Champs
    group = models.CharField(max_length=16, blank=True, db_index=True, verbose_name=_(u"Group"), help_text=_(u"Use the same name to group icons."))
    display = models.SmallIntegerField(choices=TYPES, default=0, db_index=True, help_text=_(u"Default display mode of this link"), verbose_name=_(u"Type"))
    url = models.URLField(max_length=1024, unique=True, verbose_name=_(u"URL"))
    anchor = models.CharField(max_length=192, blank=True, verbose_name=_(u"Anchor"))
    title = models.CharField(max_length=128, blank=True, verbose_name=_(u"Title"))
    target = models.CharField(max_length=16, default="_self", blank=True, verbose_name=_(u"Target"))
    nofollow = models.BooleanField(default=True, verbose_name=_(u"No-follow"))
    remainder = models.CharField(max_length=64, blank=True, verbose_name=_(u"HTML Remainder"), help_text=_(u"HTML code of extra tag attributes"))
    information = models.TextField(blank=True, default=u"", help_text=_(u"Internal information for the link"), verbose_name=_(u"Information"))
    description = models.TextField(blank=True, default=u"", verbose_name=_(u"Description"))
    objects = LinkManager()

    # Getter
    @render_to("content/display/link.html")
    def html(self):
        """ Renvoyer le code HTML du lien """
        return {'link': self}

    @addattr(boolean=True)
    def is_valid(self):
        """ Renvoyer si l'URL est formée correctement """
        parsed = urlparse.urlparse(self.url)
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
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.url

    # Métadonnées
    class Meta:
        verbose_name = _(u"link")
        verbose_name_plural = _(u"links")
        app_label = 'content'
