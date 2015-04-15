# coding: utf-8
from __future__ import absolute_import

from autoslug.fields import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.social.access import PrivacyModel
from scoop.core.abstract.social.invite import InviteTargetModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager


class GroupManager(SingleDeleteManager):
    """ Manager des groupes d'intérêt """

    # Getter
    def by_author(self, user, **kwargs):
        """ Renvoyer les groupes d'un créateur """
        return self.filter(author=user, **kwargs)

    def get_by_moderator(self, user, **kwargs):
        """ Renvoyer les groupes modérés par un utilisateur """
        return self.filter(moderators=user, **kwargs).distinct()


class Group(DatetimeModel, AuthoredModel, IconModel, PrivacyModel, UUID64Model, InviteTargetModel):
    """ Groupe d'intérêt """
    # Constantes
    MEMBERSHIPS = [(0, _(u"Anyone can join")), (1, _(u"Administrators must confirm first")), (2, _(u"Invites only"))]
    # Champs
    name = models.CharField(_(u"Name"), max_length=128, unique=True)
    slug = AutoSlugField(max_length=100, populate_from='name', unique=True, blank=True, editable=True, unique_with=('id',))
    discreet = models.BooleanField(default=False, help_text=_(u"Define if the group is not in the public listings"), verbose_name=_(u"Discrete group"))
    description = models.TextField(blank=False, verbose_name=_(u"Description"))
    membership = models.SmallIntegerField(default=0, choices=MEMBERSHIPS, verbose_name=_(u"Membership type"))
    # Membres du groupe
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='moderated_social_groups', verbose_name=_(u"Moderators"))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='social_groups', verbose_name=_(u"Members"))
    applications = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='social_groups_applied', verbose_name=_(u"Applications"))
    objects = GroupManager()

    # Getter
    def get_member_count(self):
        """ Renvoyer le nombre de membres du groupe """
        return self.users.all().count()

    def has_member(self, user):
        """ Renvoyer si un utilisateur est membre du groupe """
        return self.users.filter(id=user.id).exists()

    def has_moderator(self, user):
        """ Renvoyer si un utilisateur est modérateur du groupe """
        return self.moderators.filter(user_id=user.pk).exists()

    # Setter
    def add_member(self, user):
        """ Ajouter un membre au groupe """
        if user.has_perm('social.can_join_groups'):
            self.users.add(user)
            self.applications.filter(id=user.id).delete()
            return True
        return False

    def join(self, user):
        """ Ajouter une demande d'adhésion (ou ajouter au groupe) """
        if user.has_perm('social.can_join_groups'):
            if self.membership in [0]:
                self.add_member(user)
            elif self.membership in [1]:
                self.applications.add(user)

    def invite(self, user):
        """ Inviter un utilisateur au groupe """
        from scoop.user.social.models import Invite
        # Ajouter
        Invite.add(self, user)

    def validate(self, user):
        """ Valider la candidature d'un utilisateur """
        applications = self.applications.filter(id=user.id)
        if applications.exists():
            self.add_member(user)
            applications.delete()
            return True
        return False

    def get_args(self):
        """ Renvoyer les arguments de l'URL """
        return {'group_slug': self.slug}

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    @permalink
    def get_absolute_url(self):
        """ Renvoyer l'URL du groupe """
        return ('social:group-view', [self.uuid])

    # Métadonnées
    class Meta(object):
        verbose_name = _(u"group")
        verbose_name_plural = _(u"groups")
        permissions = (("can_join_groups", u"Can join groups"),)
        app_label = "social"
