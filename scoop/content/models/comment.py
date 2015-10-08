# coding: utf-8
from __future__ import absolute_import

import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import striptags
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from scoop.content.util.signals import comment_posted, comment_spam
from scoop.core.abstract.content.acceptable import AcceptableModel
from scoop.core.abstract.content.comment import CommentableModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.generic import GenericModel
from scoop.core.abstract.core.moderation import ModeratedModel, ModeratedQuerySetMixin
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.user.ippoint import IPPointableModel
from scoop.core.util.data.dateutil import now
from scoop.core.util.model.model import SingleDeleteQuerySetMixin
from scoop.core.util.shortcuts import addattr


class CommentQuerySetMixin(object):
    """ Mixin Queryset et Manager """

    # Getter
    def by_content(self, item):
        """ Renvoyer les commentaires liés à un objet """
        content_type = ContentType.objects.get_for_model(item)
        return self.filter(content_type=content_type, object_id=item.pk)

    def by_author(self, user):
        """ Renvoyer les commentaires postés par un utilisateur """
        return self.filter(author=user)

    # Setter
    def hide_from_author(self, author=None):
        """ Rendre invisible les contenus d'un auteur """
        if author is not None:
            return self.filter(author=author).update(visible=False)


class CommentQuerySet(models.QuerySet, CommentQuerySetMixin, SingleDeleteQuerySetMixin):
    """ Queryset des commentaires """
    pass


class CommentManager(models.Manager.from_queryset(CommentQuerySet), models.Manager, CommentQuerySetMixin, ModeratedQuerySetMixin):
    """ Manager des commentaires """

    # Setter
    def comment(self, request, author, target, body, name=None, email=None, url=None, force=False, **kwargs):
        """
        Commenter un contenu commentable
        :param request: requête (IP, utilisateur)
        :param author: auteur du commentaire
        :param target: objet cible du commentaire
        :param body: corps du commentaire
        :param name: nom de l'auteur du commentaire
        :param email: email de l'auteur du commentaire
        :param url: url de l'auteur du commentaire
        :param force: forcer la création même sur un contenu non commentable
        """
        if (isinstance(target, CommentableModel) and target.is_commentable()) or (request and request.user.is_staff) or force is True:
            comment = Comment(author=author, content_object=target, body=body, name=name or str(author), email=email or "", url=url or "")
            comment.set_request(request, save=True)
            if comment.moderated:
                comment_posted.send(sender=comment, target=target)
            return comment
        return None


class Comment(GenericModel, AcceptableModel, DatetimeModel, IPPointableModel, UUID64Model, ModeratedModel):
    """ Commentaire """
    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="comments_made", verbose_name=_("Author"))
    name = models.CharField(max_length=24, verbose_name=_("Name"))
    body = models.TextField(blank=False, verbose_name=_("Body"))
    url = models.URLField(max_length=100, blank=True, verbose_name=_("URL"))
    email = models.EmailField(max_length=64, blank=True, verbose_name=_("Email"))
    spam = models.NullBooleanField(default=None, db_index=True, verbose_name=_("Spam"))
    updated = models.DateTimeField(default=None, null=True, db_index=True, verbose_name=pgettext_lazy('comment', "Updated"))
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Updater"))
    visible = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('comment', "Visible"))
    removed = models.BooleanField(default=False, help_text=_("When visible, mark as removed"), verbose_name=pgettext_lazy('comment', "Removed"))
    objects = CommentManager()

    # Getter
    @addattr(short_description=_("URL"))
    def get_url(self):
        """ Renvoyer l'URL de l'auteur ou du commentaire """
        if self.author is not None:
            return self.author.get_absolute_url()
        else:
            return self.url

    @addattr(short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom de l'auteur ou du commentaire """
        if self.author is not None:
            return self.author.username
        return self.name if self.name != "" else _("Anonymous")

    def get_teaser(self, words=6):
        """ Renvoyer une introduction du corps du commentaire """
        return striptags(Truncator(self.body).words(words))

    def is_editable(self, request):
        """ Renvoyer si le commentaire peut être modifié par l'utilisateur """
        if request.user.is_authenticated():
            if request.user.is_staff or (self.author == request.user and now() < self.time + 600):
                return True
        return False

    @addattr(boolean=True, short_description=pgettext_lazy('comment', "Updated"))
    def is_updated(self):
        """ Renvoyer si le commentaire a été updaté """
        return self.updated > self.datetime + datetime.timedelta(seconds=30)

    def get_siblings(self, **kwargs):
        """ Renvoyer les commentaires liés au même contenu """
        return Comment.objects.filter(content_type=self.content_type, object_id=self.object_id, **kwargs)

    # Setter
    def reparent(self, parent):
        """ Déplacer le commentaire vers une nouvelle cible """
        if parent.content_object == self.content_object:
            self.move(parent)

    def set_spam(self, value=True):
        """ Définir le commentaire comme étant un spam """
        if self.spam != value:
            self.spam = value
            comment_spam.send(self, spam=value)

    def set_request(self, request, save=True):
        from scoop.user.access.models.ip import IP

        self.ip = IP.objects.get_by_request(request) if request is not None else None
        if save is True:
            self.save()

    def moderate_accept(self, save=False):
        """ Accepter le commentaire """
        super().moderate_accept(save=save)
        comment_posted.send(sender=self, target=self.content_object)

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _('{name} says: "{teaser}..."').format(name=self.get_name(), teaser=self.get_teaser())

    def __html__(self):
        """ Renvoyer la représentation HTML de l'objet"""
        return "<span>{teaser}</span>".format(teaser=self.get_teaser())

    def get_absolute_url(self):
        """ Renvoyer l'URL de l'objet """
        return self.content_object.get_absolute_url()

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.content_type = None
        self.object_id = None
        super(Comment, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """ Enregistrer le commentaire dans la base de données """
        if self.name == "":
            if self.author is not None:
                self.name = self.author.username
        self.updated = timezone.now()
        super(Comment, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        permissions = (("can_edit_own_comment", "Can edit own Comment"),)
        app_label = 'content'
