# coding: utf-8
from autoslug.fields import AutoSlugField
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.content.models.content import Content
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.icon import IconModel

__all__ = ['Tag']


class TagQuerySet(models.QuerySet):
    """ Manager des étiquettes de contenu """

    # Getter
    def in_group(self, name):
        """ Renvoyer les tags appartenant à un groupe """
        return self.filter(group__iexact=name)

    def get_by_slug(self, slug, exc=None):
        """
        Renvoyer le tag correspondant à un slug
        
        :param slug: slug du tag
        :param exc: exception à lever lorsque la récupération échoue, None remonte normalement
        """
        try:
            return self.get(short_name=slug)
        except Tag.DoesNotExist:
            if exc is not None:
                raise exc
            raise



class Tag(IconModel, PicturableModel):
    """ Étiquette de contenu """

    # Champs
    group = models.CharField(max_length=16, blank=True, verbose_name=_("Group"))
    category = models.ForeignKey('content.Category', null=True, help_text=_("Category if this tag is specific to one"), verbose_name=_("Category"))
    name = models.CharField(max_length=96, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    short_name = AutoSlugField(max_length=100, populate_from='name', unique=True, blank=True, editable=True, unique_with=('id',), verbose_name=_("Short name"))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_("Parent"))
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('tag', "Active"))
    objects = TagQuerySet.as_manager()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    # Getter
    def get_absolute_url(self):
        """ Renvoyer l'URL de l'objet """
        return reverse_lazy('content:view-category', args=[self.short_name])

    def get_children(self):
        """ Renvoyer les étiquettes enfants """
        return self.children.all()

    def get_content_count(self):
        """ Renvoyer le nombre de contenus portant cette étiquette """
        return Content.objects.filter(tags=self).distinct().count()

    def get_tree(self):
        """ Renvoyer la hiérarchie de l'étiquette """
        item = self
        output = [self]
        while item.parent is not None:
            item = item.parent
            output.append(item)
        return output.reverse()

    # Overrides
    def save(self, *args, **kwargs):
        """ Sauvegarder l'objet """
        if self.parent == self:
            self.parent = None
        super().save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        unique_together = (('short_name', 'category'),)
        ordering = ['name']
        app_label = 'content'
