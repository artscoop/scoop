# coding: utf-8
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.expressions import F
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.data.dateutil import now


class VisitManager(models.Manager):
    """ Manager des visites de profils """

    # Getter
    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(VisitManager, self).get_queryset()

    def to_user(self, user, as_users=False):
        """ Renvoyer les visites faites à un utilisateur, ou les visiteurs """
        if as_users is False:
            return self.select_related('visitor').only('visitor', 'time').filter(user=user).order_by('-time')
        # Renvoyer les utilisateurs, avec un champ timestamp when
        return get_user_model().objects.active().filter(visits_maker__user=user).annotate(when=F('visits_receiver__time'))

    def by_user(self, user, as_users=False):
        """ Renvoyer les visites faites par un utilisateur, ou les utilisateurs vus """
        if as_users is False:
            return self.select_related('user').only('user', 'time').filter(visitor=user).order_by('-time')
        # Renvoyer les utilisateurs, avec un champ timestamp when
        return get_user_model().objects.active().filter(visits_receiver__visitor=user).annotate(when=F('visits_receiver__time'))

    def has_visitors(self, user):
        """ Renvoyer si un utilisateur a eu des visiteurs """
        return self.filter(user=user).exists()

    def has_made_visits(self, user):
        """ Renvoyer si un utilisateur a vu d'autres profils """
        return self.filter(visitor=user).exists()

    # Setter
    def new(self, visitor, target_user):
        """ Consigner ou mettre à jour une visite à un profil """
        if visitor.pk != target_user.pk:
            if self.filter(visitor=visitor, user=target_user).update(time=now()) == 0:
                return self.create(visitor=visitor, user=target_user, time=now())
            return True
        return False

    def wipe_visitor(self, user):
        """ Supprimer toutes les visites qu'un utilisateur a faites """
        self.filter(visitor=user).delete()

    def wipe_visitee(self, user):
        """ Supprimer toutes les visites reçues par un utilisateur """
        self.filter(user=user).delete()

    def prune(self, days=120):
        """ Supprimer les visites plus anciennes que n jours """
        timestamp = now() - days * 86400
        self.filter(time__lt=timestamp).delete()


class Visit(DatetimeModel):
    """ Visite de profil """

    # Champs
    visitor = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='visits_maker', verbose_name=_("Visitor"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='visits_receiver', verbose_name=_("User"))
    objects = VisitManager()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "{visitor} -> {target}".format(visitor=self.visitor, target=self.user)

    # Métadonnées
    class Meta:
        verbose_name = _("profile visit")
        verbose_name_plural = _("profile visits")
        unique_together = (('visitor', 'user'),)
        # Pas de traduction paresseuse des permissions (https://code.djangoproject.com/ticket/13965)
        permissions = (("can_ghost_visit", "Can visit stealth"),)
        app_label = 'user'
