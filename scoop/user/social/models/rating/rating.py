# coding: utf-8
import random

from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import ContentType, GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.aggregates import Avg, Count, Sum
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.data.uuid import uuid_bits
from scoop.core.util.model.model import SingleDeleteManager, limit_to_model_names
from scoop.core.util.shortcuts import addattr
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model


class Axis(TranslatableModel, WeightedModel):
    """ Axe de notation """

    # Champs
    slug = models.SlugField(max_length=32, unique=True, blank=False, default=uuid_bits, verbose_name=_("Slug"))
    limit = limit_to_model_names('user.user', 'content.content', 'content.picture')
    content_type = models.ForeignKey('contenttypes.ContentType', null=False, blank=False, limit_choices_to=limit, verbose_name=_("Content type"))

    # Getter
    @addattr(short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom de la catégorie """
        try:
            return self.get_translation().name
        except MissingTranslation:
            return _("(No name)")

    @addattr(short_description=_("Description"))
    def get_description(self):
        """ Renvoyer la description de la catégorie """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _("(No description)")

    # Propriétés
    name = property(get_name)
    description = property(get_description)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{name}").format(name=self.name)

    class Meta:
        """ Métadonnées """
        verbose_name = _("rating axis")
        verbose_name_plural = _("rating axes")
        app_label = 'social'


class AxisTranslation(get_translation_model(Axis, "axis"), TranslationModel):
    """ Traduction d'axe de notation """

    # Champs
    name = models.CharField(max_length=32, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Métadonnées
    class Meta:
        app_label = 'social'


class RatingManager(SingleDeleteManager):
    """ Manager des notes """

    # Setter
    def rate(self, author, item, value, axis=None):
        """ Ajouter une note à un objet """
        rating = Rating(content_object=item, value=value, author=author, axis=axis)
        rating.save()

    def unrate(self, author, item):
        """ Retirer une note à un objet """
        content_type = ContentType.objects.get_for_model(item)
        self.filter(author=author, content_type=content_type, id=item.pk).delete()


class Rating(DatetimeModel):
    """ Note donnée par un utilisateur à un objet arbitraire """

    # Champs
    axis = models.ForeignKey('social.Axis', blank=True, null=True, related_name='ratings', verbose_name=_("Axis"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='ratings_given', verbose_name=_("Author"))
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0, verbose_name=_("Rating"))
    limit = models.Q(name__in=['Content'])  # limitation des modèles cibles
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, db_index=True, verbose_name=_("Content type"), limit_choices_to=limit)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True, verbose_name=_("Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    objects = RatingManager()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{user} gave {item} {rating:.03f} points").format(rating=self.rating, item=self.content_object, user=self.author)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.content_type = None
        self.object_id = None
        super(Rating, self).delete(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("rating")
        verbose_name_plural = _("ratings")
        unique_together = [['author', 'axis', 'content_type', 'object_id']]
        app_label = 'social'


class RatedModel(models.Model):
    """ Mixin d'objet pouvant recevoir des notes """

    # Champs
    ratings = GenericRelation('social.Rating')

    # Setter
    def rate(self, author, value, axis=None):
        """ Ajouter une note """
        rating = Rating(content_object=self, value=value, author=author, axis=axis)
        rating.save()

    def unrate(self, author):
        """ Retirer une note """
        content_type = ContentType.objects.get_for_model(self)
        Rating.objects.filter(content_type=content_type, id=self.pk).delete()

    # Getter
    def get_rating_average(self, axis=None):
        """ Renvoyer la note moyenne sur un axe """
        ratings = self.ratings.all()
        if axis is not None:
            ratings = ratings.filter(axis=axis)
        result = ratings.aggregate(Avg('rating'))
        return result['rating__avg']

    def get_rating_sum(self, axis=None):
        """ Renvoyer la somme des notes sur un axe """
        ratings = self.ratings.all()
        if axis is not None:
            ratings = ratings.filter(axis=axis)
        result = ratings.aggregate(Sum('rating'))
        return result['rating__sum']

    def get_rating_count(self, axis=None, values=None):
        """ Renvoyer le nombre de notes sur un axe """
        ratings = self.ratings.all()
        if axis is not None:
            ratings = ratings.filter(axis=axis)
        if values is not None:
            ratings = ratings.filter(rating__range=values)
        return ratings.count()

    def get_rating_counts(self, axis=None):
        """ Renvoyer le nombre de votes par note """
        criteria = {'axis': axis} if axis is not None else {}
        data = self.ratings.filter(**criteria).values('rating').annotate(count=Count('rating'))
        return data

    # Métadonnées
    class Meta:
        abstract = True
