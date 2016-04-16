# coding: utf-8

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import ContentType, GenericRelation
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.fileutil import asset_file


class CommentableModel(models.Model):
    """ Objet pouvant recevoir et gérer des commentaires """

    # Champs
    commentable = models.BooleanField(default=True, verbose_name=_("Commentable"))
    comment_count = models.IntegerField(default=0, verbose_name=_("Comments"))
    comments = GenericRelation('content.Comment')

    # Getter
    def get_latest_comment(self):
        """ Renvoyer le commentaire le plus récent """
        comments = self.comments.filter(visible=True)
        return comments.latest('id') if comments.exists() else None

    def get_first_comment(self):
        """ Renvoyer le commentaire le plus ancien """
        comments = self.comments.filter(visible=True).order_by('id')
        return comments.earliest('id') if comments.exists() else None

    @addattr(short_description=mark_safe('<img src="{path}">'.format(path=asset_file('icons', 'black', 'chat_bubble_message_square_icon&16.png'))))
    def get_comments(self, reverse=False):
        """ Renvoyer les commentaires de l'objet """
        result = self.comments.select_related().filter(visible=True)
        return result.order_by('time' if reverse else '-time')

    @addattr(short_description=mark_safe('<img src="{path}">'.format(path=asset_file('icons', 'black', 'chat_bubble_message_square_icon&16.png'))))
    def get_comment_count(self, cached=False):
        """ Renvoyer le nombre de commentaires de l'objet """
        return self.comments.filter(visible=True).count() if not cached else self.comment_count

    @addattr(allow_tags=True, short_description=mark_safe('<center title="{label}">&#x1f5db;</center>'.format(label=_("Comments"))))
    def get_comment_count_admin(self):
        """ Renvoyer le nombre de commentaires (pour l'admin) """
        return "<center><span class='badge'>{count}</span></center>".format(count=self.get_comment_count())

    @addattr(boolean=True, short_description=_("Comments"))
    def has_comments(self):
        """ Renvoyer si l'objet possède des commentaires """
        return self.comments.exists()

    @addattr(boolean=True, short_description=_("Commentable"))
    def is_commentable(self):
        """ Renvoyer si le contenu peut être commenté """
        return self.commentable

    def get_commenters(self):
        """ Renvoyer les utilisateurs ayant commenté l'objet """
        content_type = ContentType.objects.get_for_model(self)
        return get_user_model().objects.by_request().filter(author_comment__content_type=content_type, author_comment__object_id=self.pk,
                                                            author_comment__visible=True).distinct()

    # Setter
    def set_commentable(self, commentable=True):
        """ Définir l'objet comme commentable ou non """
        if self.commentable != commentable:
            self.commentable = commentable
            self.save(update_fields=['commentable'])

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.comment_count = self.get_comment_count()
        super(CommentableModel, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        abstract = True
