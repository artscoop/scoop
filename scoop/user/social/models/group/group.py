# coding: utf-8
from autoslug.fields import AutoSlugField
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.db.models import Q
from django.db.models.manager import Manager
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.social.access import PrivacyModel
from scoop.core.abstract.social.invite import InviteTargetModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteQuerySetMixin


class GroupQuerySetMixin(object):
    # Mixin de Queryset des groupes

    # Getter
    def discreet(self):
        """ Renvoyer les groupes invisibles au public """
        return self.filter(discreet=True)

    def by_author(self, user, **kwargs):
        """ Renvoyer les groupes d'un créateur """
        return self.filter(author=user, **kwargs)

    def by_moderator(self, user, **kwargs):
        """ Renvoyer les groupes modérés par un utilisateur """
        return self.filter(moderators=user, **kwargs).distinct()

    def by_membership(self, membership, **kwargs):
        """ Renvoyer les groupes modérés par un utilisateur """
        return self.filter(membership=membership, **kwargs).distinct()

    def by_request(self, request):
        """ Renvoyer les groupes visibles pour la requête en cours """
        user = request.user
        if user.is_authenticated() and not user.is_staff:
            return self.filter(Q(author=user) | Q(discreet=False))
        elif user.is_staff:
            return self.all()
        elif user.is_anonymous():
            return self.filter(discreet=False, private=False)


class GroupQuerySet(models.QuerySet, GroupQuerySetMixin, SingleDeleteQuerySetMixin):
    """ Queryset des groupes """
    pass


class GroupManager(Manager.from_queryset(GroupQuerySet), models.Manager, GroupQuerySetMixin):
    """ Manager des groupes d'intérêt """
    pass


class Group(DatetimeModel, AuthoredModel, IconModel, PrivacyModel, DataModel, UUID64Model, InviteTargetModel):
    """ Groupe d'intérêt """

    # Constantes
    MEMBERSHIPS = [(0, _("Anyone can join")), (1, _("Administrators must confirm first")), (2, _("Invites only"))]
    DATA_KEYS = ['privacy']

    # Champs
    name = models.CharField(_("Name"), max_length=128, unique=True)
    slug = AutoSlugField(max_length=100, populate_from='name', unique=True, blank=True, editable=True, unique_with=('id',))
    discreet = models.BooleanField(default=False, help_text=_("Define if the group is not in the public listings"), verbose_name=_("Discrete group"))
    private = models.BooleanField(default=False, verbose_name=_("Private"))
    description = models.TextField(blank=False, verbose_name=_("Description"))
    membership = models.SmallIntegerField(default=0, choices=MEMBERSHIPS, verbose_name=_("Membership type"))

    # Membres du groupe
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='moderated_social_groups', verbose_name=_("Moderators"))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='social_groups', verbose_name=_("Members"))
    applications = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='social_groups_applied', verbose_name=_("Applications"))
    objects = GroupManager()

    # Getter
    def is_visible(self, request_or_user):
        """ Renvoyer si le groupe est accessible à un utilisateur """
        user = getattr(request_or_user, 'user', request_or_user)
        return self.private is False or user in self.users.all() or user in self.applications.all()

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
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    def get_absolute_url(self):
        """ Renvoyer l'URL du groupe """
        return reverse_lazy('social:group-view', args=[self.uuid])

    # Métadonnées
    class Meta(object):
        verbose_name = _("group")
        verbose_name_plural = _("groups")
        permissions = [["can_join_groups", "Can join groups"],
                       ["can_toggle_groups", "Can change group visibility"]]
        app_label = "social"
