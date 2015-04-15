# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.http import HttpRequest
from django.template.base import TemplateDoesNotExist, TextNode
from django.template.context import RequestContext
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.shortcuts import addattr


class Template(DatetimeModel):
    """ Template d'affichage d'une page """
    # Champs
    name = models.CharField(max_length=32, unique=True, blank=False, verbose_name=_(u"Name"))
    path = models.CharField(max_length=64, blank=False, unique=True, verbose_name=_(u"Path"))
    full = models.BooleanField(default=False, help_text=_(u"Contains html, head and body tags."), verbose_name=_(u"Full page template"))
    positions = models.ManyToManyField('editorial.Position', blank=True, verbose_name=_(u"Positions"))

    # Actions
    def auto_fill(self):
        """ Créer automatiquement les positions présentes dans le template """
        from scoop.editorial.models.position import Position
        # Parcourir
        try:
            template = get_template(self.path)
            # Créer les emplacements
            for name in Template._get_block_names(template):
                position = Position.get(name)
                self.positions.add(position)
            # Définir si le template est une page HTML ou non
            self.full = True if Template._find_html_tags(template, ['html', 'head', 'body']) else False
            self.save()
        except:
            pass

    # Getter
    @addattr(boolean=True, short_description=_(u"File exists"))
    def exists(self):
        """ Renvoyer si le chemin de template est valide """
        try:
            get_template(self.path)
            return True
        except TemplateDoesNotExist:
            return False

    @staticmethod
    def _get_block_names(template):
        """ Générer la liste des noms de blocs d'un template """
        nodelist = template.nodelist
        extendlist = nodelist.get_nodes_by_type(ExtendsNode)
        if len(extendlist) > 0:
            for block in extendlist[0].blocks:
                yield block
            for item in Template._get_block_names(extendlist[0].get_parent(RequestContext(HttpRequest()))):
                yield item
        else:
            nodelist = template.nodelist
            for node in nodelist:
                if isinstance(node, BlockNode):
                    yield node.name

    @staticmethod
    def _find_html_tags(template, tags, find_all=True):
        """ Renvoyer si des tags HTML existent dans le template """
        nodelist = template.nodelist
        extendlist = nodelist.get_nodes_by_type(ExtendsNode)
        textlist = nodelist.get_nodes_by_type(TextNode)
        if len(extendlist) > 0:
            return False or Template._find_html_tags(extendlist[0].get_parent(RequestContext(HttpRequest())), tags)
        elif len(textlist) > 0:
            for text in textlist:
                tags_found = {tag.lower() for tag in tags if (u'<{}>'.format(tag)) in text.s}
                if tags_found and (not find_all or len(tags_found) == len(tags)):
                    return True
            return False

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return u"{name} ({count})".format(name=self.name, count=self.positions.count())

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Template, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _(u"template")
        verbose_name_plural = _(u"templates")
        app_label = 'editorial'
