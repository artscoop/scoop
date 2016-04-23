# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.social.access import PrivacyModel
from scoop.core.abstract.social.like import LikableModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.data.dateutil import now
from scoop.core.util.model.model import SingleDeleteManager


class PostManager(SingleDeleteManager):
    """ Manager des posts """

    # Getter
    def get_latest(self, user):
        """ Renvoyer le dernier post d'un utilisateur """
        return self.filter(author=user).order_by('-id').first()

    def get_count_for(self, user):
        """ Renvoyer le nombre de posts d'un utilisateur """
        return self.filter(author=user).count()

    # Setter
    def add(self, user, text, purge=0):
        """ Ajouter un post pour un utilisateur """
        self.create(author=user, text=text)
        # Purger les posts anciens de n+ jours
        if purge > 0:
            limit = now() - 86400 * purge
            posts = self.filter(author=user, time__lte=limit).delete()
            return posts
        return True


class Post(DatetimeModel, AuthoredModel, PrivacyModel, LikableModel):
    """ Post """
    # Champs
    text = models.CharField(max_length=140, verbose_name=_("Text"))
    deleted = models.BooleanField(default=False, verbose_name=_("Deleted"))
    objects = PostManager()

    # Overrides
    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.deleted = True
        self.save(update_fields=['deleted'])

    # Métadonnées
    class Meta(object):
        verbose_name = _("user shout")
        verbose_name_plural = _("user shouts")
        app_label = "social"
