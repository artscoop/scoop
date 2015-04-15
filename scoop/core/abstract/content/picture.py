# coding: utf-8
from __future__ import absolute_import

from traceback import print_exc

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.moderation import ModeratedModel


class PicturedBaseModel(models.Model):
    """ Objet étant lié à des images via ManyToMany ou Generic """
    PICTURE_FILTERING = getattr(settings, 'GENERICRELATION_PICTURE_FILTER', {'moderated': True})
    # Getter
    def get_pictures(self, exclude=None, filtering=PICTURE_FILTERING, reverse=False):
        """ Renvoyer les images liées à l'objet """
        pictures = self.pictures.order_by('{sign}weight'.format(sign='-' if reverse else '')).filter(**filtering).exclude(**(exclude or {}))
        return pictures

    def get_picture_count(self, exclude=None, filtering=PICTURE_FILTERING):
        """ Renvoyer le nombre d'images liées à l'objet """
        pictures = self.pictures.filter(**filtering).exclude(**(exclude or {}))
        return pictures.count()

    def has_pictures(self, filtering=PICTURE_FILTERING):
        """ Renvoyer si l'objet est lié à des images """
        return self.pictures.filter(**filtering).exists()

    def get_latest_picture(self):
        """ Renvoyer l'image la plus récente de l'objet """
        return self.get_pictures().order_by('-updated')[0]

    def get_earliest_picture(self):
        """ Renvoyer l'image la plus ancienne de l'objet """
        return self.get_pictures().order_by('updated')[0]

    def get_last_pictures(self, count=3):
        """ Renvoyer les n dernières images de l'objet """
        return self.pictures.order_by('-id')[0:count]

    def _fetch_pictures(self, default, fallback, count, author=None, force=False):
        """
        Télécharger automatiquement des images pour une expression
        :param default: expression de recherche par défaut
        :param fallback: expression de recherche en cas d'échec
        :param count: nombre d'images à télécharger au maximum
        """
        from scoop.content.models import Picture
        from scoop.user.models import User
        # Quitter si des images existent et que l'opération n'est pas forcée
        if not force and self.has_pictures():
            return 0
        # Parcourir
        actually_downloaded = 0
        images = Picture.objects.find_by_keyword(default) or Picture.objects.find_by_keyword(fallback)
        for number, image in enumerate(images[0:count], start=1):
            description = u"{name} ({index})".format(name=self.get_name(), index=number)
            try:
                if isinstance(self, PicturableModel):
                    picture = Picture.objects.create_from_uri(image['url'], content_object=self, title=description, description=image['title'], author=author or User.objects.get_superuser())
                elif isinstance(self, PicturedModel):
                    picture = Picture.objects.create_from_uri(image['url'], title=description, description=image['title'], author=author or User.objects.get_superuser())
                    if picture is not None:
                        self.pictures.add(picture)
                if picture is not None:
                    actually_downloaded += 1
                    if issubclass(Picture, ModeratedModel):  # Modérer automatiquement
                        Picture.objects.filter(id=picture.id, moderated__isnull=True).update(moderated=True)
            except Exception, e:
                print_exc(e)
        if actually_downloaded > 0 or self.has_pictures({}):
            self.pictured = True
            self.save()
        return actually_downloaded

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.pictured = bool(self.has_pictures()) or (hasattr(self, 'picture') and self.picture is not None and self.picture.moderated is True)
        super(PicturedBaseModel, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        abstract = True


class PicturableModel(PicturedBaseModel):
    """ Objet pouvant être lié à des images via une relation générique """
    # Champs
    pictured = models.BooleanField(default=False, db_index=True, verbose_name=_(u"\U0001f58c"))
    pictures = GenericRelation('content.Picture')

    # Métadonnées
    class Meta:
        abstract = True


class PicturedModel(PicturedBaseModel):
    """ Objet lié à des images par un champ ManyToMany """
    # Champs
    pictured = models.BooleanField(default=False, db_index=True, verbose_name=_(u"\U0001f58c"))
    pictures = models.ManyToManyField('content.Picture', blank=True, verbose_name=_(u"Pictures"))

    # Métadonnées
    class Meta:
        abstract = True
