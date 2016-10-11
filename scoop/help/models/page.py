# coding: utf-8
from markdown import markdown

from autoslug.fields import AutoSlugField
from django.db import models
from django.template import Template
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.shortcuts import addattr
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model


class PageManager(models.Manager):
    """ Manager de l'aide """

    # Getter
    def get_by_uuid(self, uuid):
        """ Renvoyer une page portant un UUID """
        return self.get(uuid=uuid)


class Page(DatetimeModel, UUID64Model, TranslatableModel, WeightedModel):
    """
    Page d'aide

    Les pages d'aide sont au format Markdown, avec la possibilité
    d'utiliser le rendu HTML comme un template Django.
    """

    # Champs
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('page', "Active"))
    groups = models.ManyToManyField('help.helpgroup', blank=True, verbose_name=_("Groups"))
    slug = models.SlugField(max_length=128, blank=False, verbose_name=_("Slug"))
    path = models.CharField(max_length=64, blank=True, verbose_name=_("Path"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('page', "Updated"))
    keywords = models.CharField(max_length=128, blank=True, verbose_name=_("Keywords"))
    objects = PageManager()

    # Getter
    @addattr(short_description=_("Text"))
    def get_text(self):
        """ Renvoyer la description de l'option """
        try:
            return self.get_translation().text
        except MissingTranslation:
            return _("(No text)")

    @addattr(short_description=_("Title"))
    def get_title(self):
        """ Renvoyer le titre de la page """
        try:
            return self.get_translation().title
        except MissingTranslation:
            return _("(No title)")

    def render_html(self, request=None):
        """
        Renvoyer la version HTML du texte de l'aide

        Rend en premier lieu la version HTML du Markdown de la page.
        Puis rend la version HTML comme un template Django.
        """
        html_version = markdown(self.text)
        template = Template(html_version)
        context = RequestContext(request)
        output = template.render(context)
        return output

    # Propriétés
    text = property(get_text)
    title = property(get_title)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation de l'objet """
        return "help page - {0}".format(self.slug)

    # Métadonnées
    class Meta:
        verbose_name = _("Help page")
        verbose_name_plural = _("Help pages")
        app_label = 'help'


class PageTranslation(get_translation_model(Page, "page"), TranslationModel):
    """ Traduction des pages """

    # Champs
    title = models.CharField(max_length=128, blank=False, verbose_name=_("Title"))
    text = models.TextField(blank=False, help_text=_("Markdown"), verbose_name=_("Text"))

    # Métadonnées
    class Meta:
        app_label = 'help'
