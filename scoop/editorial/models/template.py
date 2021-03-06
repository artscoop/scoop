# coding: utf-8
import os

from django.db import models
from django.template.base import TextNode
from django.template.context import Context
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template, select_template
from django.template.loader_tags import BlockNode, ExtendsNode
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.shortcuts import addattr


class TemplateQuerySet(models.QuerySet):
    """ Queryset des templates """

    # Getter
    def get_by_natural_key(self, path):
        """ Clé naturelle """
        return self.get(path=path)


class Template(DatetimeModel):
    """ Template d'affichage d'une page """

    # Champs
    name = models.CharField(max_length=32, unique=True, blank=False, verbose_name=_("Name"))
    path = models.CharField(max_length=128, blank=False, unique=True, verbose_name=_("Path"))
    full = models.BooleanField(default=False, help_text=_("Contains html, head and body tags."), verbose_name=_("Full page template"))
    positions = models.ManyToManyField('editorial.Position', blank=True, verbose_name=_("Positions"))
    objects = TemplateQuerySet.as_manager()

    # Raccourcis
    @staticmethod
    def at_path(path, name=None):
        """
        Renvoyer l'objet Template correspondant au chemin de template
        
        :param path: chemin du template django
        :param name: nom assigné au template
        :return: un objet Template, ou None si aucun template Django n'existe au chemin indiqué
        """
        try:
            paths = path.split(',')
            select_template(paths)
            name = os.path.basename(paths[0]) if name is None else name
            template, _ = Template.objects.get_or_create(name=name, path=path)
            return template
        except TemplateDoesNotExist:
            return None

    # Actions
    def auto_fill(self):
        """ Créer automatiquement les positions présentes dans le template """
        from scoop.editorial.models.position import Position
        # Parcourir
        try:
            template = select_template(self.get_paths())
            # Créer les emplacements
            for name in Template._get_block_names(template):
                position = Position.get(name)
                self.positions.add(position)
            # Définir si le template est une page HTML ou non
            full = True if Template._find_html_tags(template, ['html', 'head', 'body']) else False
            if self.full != full:
                self.full = full
                Template.objects.filter(pk=self.pk).update(full=full)
        except ValueError:
            pass

    # Getter
    @addattr(boolean=True, short_description=_("File exists"))
    def exists(self):
        """ Renvoyer si le chemin de template est valide """
        try:
            select_template(self.get_paths())
            return True
        except TemplateDoesNotExist:
            return False

    @addattr(boolean=True, short_description=_("Has inner blocks"))
    def has_positions(self):
        """ Renvoyer si des blocs existent dans le template """
        return self.positions.exists()

    def has_position(self, name):
        """
        Renvoyer si des blocs existent dans le template
        
        :param name: nom du bloc de position à retrouver
        :returns: True si le bloc existe dans le template
        :rtype: bool
        """
        return self.positions.filter(name=name).exists()

    @addattr(short_description=_("Inner blocks"))
    def get_positions(self):
        """
        Renvoyer les blocs existent dans le template
        
        :returns: un queryset de toutes les positions recensées dans l'objet
        :rtype: django.db.models.QuerySet
        """
        return self.positions.all()

    def get_position(self, name):
        """
        Renvoyer la position portant un nom
        
        :param name: nom du bloc de position
        :returns: un objet Position, ou None si aucun ne correspond dans ce template
        :rtype: scoop.editorial.models.Template
        """
        from scoop.editorial.models import Position
        try:
            return self.positions.get(name=name)
        except Position.DoesNotExist:
            return None

    def get_paths(self):
        """
        Renvoyer les chemins de templates
        
        :returns: une liste de chemins de templates
        :rtype: list<str>
        """
        return self.path.split(',')

    @addattr(short_description=_("Inner blocks"))
    def get_position_count(self):
        """
        Renvoyer le nombre de blocs existant dans le template
        
        rtype: int
        """
        return self.positions.count()

    @staticmethod
    def _get_block_names(template):
        """
        Générer la liste des noms de blocs d'un template
        
        :rtype: generator<string>
        """
        nodelist = template.template.nodelist
        extendlist = nodelist.get_nodes_by_type(ExtendsNode)
        if len(extendlist) > 0:
            for block in extendlist[0].blocks:
                yield block
            parent_template = get_template(extendlist[0].parent_name.resolve(Context({})))
            for item in Template._get_block_names(parent_template):
                yield item
        else:
            nodelist = template.template.nodelist
            for node in nodelist:
                if isinstance(node, BlockNode):
                    yield node.name

    @staticmethod
    def _find_html_tags(template, tags, find_all=True):
        """
        Renvoyer si des tags HTML existent dans le template
        
        :param find_all: Ne renvoyer True que si *toutes* les balises sont trouvées
        :param tags: liste des balises html à trouver
        :param template: objet template Django
        :returns: True si une/toutes les balises ont été trouvées
        """
        nodelist = template.template.nodelist
        extendlist = nodelist.get_nodes_by_type(ExtendsNode)
        textlist = nodelist.get_nodes_by_type(TextNode)
        if len(extendlist) > 0:
            parent_template = get_template(extendlist[0].parent_name.resolve(Context({})))
            return False or Template._find_html_tags(parent_template, tags)
        elif len(textlist) > 0:
            tags_found = set()
            for text in textlist:
                tags_found.update({tag.lower() for tag in tags if ('</{0}>'.format(tag)) in text.s})
            if tags_found and (not find_all or len(tags_found) == len(tags)):
                return True
        return False

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "{name} ({count})".format(name=self.name, count=self.positions.count())

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Template, self).save(*args, **kwargs)
        self.auto_fill()

    # Métadonnées
    class Meta:
        verbose_name = _("template")
        verbose_name_plural = _("templates")
        app_label = 'editorial'
