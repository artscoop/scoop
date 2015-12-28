# coding: utf-8
from django.core.cache import cache
from django.db import models
from django.template.base import Template
from django.template.context import RequestContext
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.seo.index import SEIndexModel
from scoop.core.abstract.user.authored import AuthoredModel
from unidecode import unidecode


class PageManager(models.Manager):
    """ Manager des pages """

    # Getter
    def active(self):
        """ Renvoyer les pages actives """
        return self.filter(active=True)

    def get_path_set(self):
        """ Renvoyer la liste des URLs de pages """
        return self.active().values_list('path', flat=True)

    def get_page(self, request):
        """ Renvoyer la page à une URL, ou None """
        # Définir l'URL à rechercher
        url = request.path if request.path.startswith('/') else ('/' + request.path)
        # Trouver les pages à l'URL
        pages = self.filter(path__iexact=url, active=True)
        return pages[0] if pages.exists() else None


class Page(WeightedModel, DatetimeModel, AuthoredModel, UUID64Model, SEIndexModel):
    """ Page personnalisée """
    # Champs
    name = models.CharField(max_length=64, unique=True, blank=False, verbose_name=_("Name"))
    title = models.CharField(max_length=64, blank=False, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    keywords = models.CharField(max_length=160, blank=True, verbose_name=_("Keywords"))
    path = models.CharField(max_length=160, help_text=_("Page URL"), verbose_name=_("Path"))
    template = models.ForeignKey('editorial.Template', blank=False, null=False, related_name='pages', limit_choices_to={'full': True}, verbose_name=_("Template"))
    active = models.BooleanField(default=True, blank=True, verbose_name=pgettext_lazy('page', "Active"))
    heading = models.TextField(blank=True, verbose_name=_("Page header extra code"))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', help_text=_("Parent page, used in lists and breadcrumbs"), verbose_name=_("Parent"))
    # Accès
    anonymous = models.BooleanField(default=True, blank=True, verbose_name=_("Anonymous access"))
    authenticated = models.BooleanField(default=True, blank=True, verbose_name=_("Authenticated access"))
    objects = PageManager()

    # Getter
    def render(self, request):
        """ Rendre la page """
        cache_key = 'editorial.page.render.{id}'.format(id=self.id)
        output = cache.get(cache_key, [])
        if output is not []:
            return output
        # Ligne extends
        extends = '{{{{% extends "{path}" %}}}}'.format(path=self.template.path)
        filters = '{% load i18n panels inlines %}'
        output.append(extends)
        output.append(filters)
        # Blocs
        for position in self.position_set.all():
            if position.has_access(request.user):
                content = "{{block.super}}"
                # Récupérer les configurations appartenant à ce block
                for configuration in self.get_configurations(position).iterator():
                    content += configuration.render()
                output.append("{{{{% block {name} %}}}}{content}{{{{% endblock %}}}}".format(name=position.name, content=content))
        # Utiliser le rendu comme un template
        output = "".join(output)
        template = Template(output)
        context = RequestContext(request, {'page': self})
        page_html = template.render(context)
        cache.set(cache_key, page_html)
        return page_html

    def get_children(self, active=True):
        """ Renvoyer les pages enfants """
        criteria = {'active': True} if active else {}
        return Page.objects.filter(parent=self, **criteria)

    def get_configurations(self, position):
        """ Renvoyer les configurations dans cette page à une position """
        return self.configurations.filter(position=position).order_by('weight')

    def is_visible(self, request):
        """ Renvoyer si la page est accessible à l'utilisateur courant """
        if self.active and (self.anonymous and request.user.is_anonymous()) or (self.authenticated and request.user.is_authenticated()):
            return True
        return False

    def get_absolute_url(self):
        """ Renvoyer l'URL de la page """
        return self.path

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.path = unidecode(self.path).lower()
        super(Page, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        app_label = 'editorial'
