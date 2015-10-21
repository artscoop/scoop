# coding: utf-8
from __future__ import absolute_import

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import ContentType, GenericRelation
from django.db import models


class LikableModel(models.Model):
    """ Objet qui peut être liké """
    # Champs
    likers = GenericRelation('social.Like')

    # Getter
    def get_like_count(self):
        """ Renvoyer le nombre de likes sur l'objet """
        return self.likers.all().count()

    def get_likers(self):
        """ Renvoyer les utilisateurs ayant liké l'objet """
        content_type = ContentType.objects.get_for_model(self)
        return get_user_model().objects.filter(like__content_type=content_type, like__object_id=self.pk)

    def has_liker(self, user):
        """ Renvoyer si l'utilisateur a liké l'objet """
        return self.likers.filter(author=user).exists()

    # Setter
    def do_like(self, author):
        """ Définir le contenu comme liké par un utilisateur """
        from scoop.user.social.models.rating.like import Like
        Like.objects.like(self, author)

    # Métadonnées
    class Meta:
        abstract = True
