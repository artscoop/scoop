# coding: utf-8
from random import choice

from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.data import DataModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.user.social.util.signals import friend_accepted, friend_denied, friend_pending_new


class FriendListManager(SingleDeleteManager):
    """ Manager des listes d'amis """

    # Getter
    def get_friend_ids(self, user):
        """ Renvoyer les ids des amis d'un utilisateur """
        return user.friends.get_friend_ids()

    def exists(self, recipient, sender):
        """ Renvoyer si deux utilisateurs sont amis """
        return recipient == sender or sender.pk in self.get_friend_ids(recipient)

    def by_user(self, user):
        """ Renvoyer l'objet liste d'amis d'un utilisateur """
        return self.get(user=user)

    # Setter
    def add_pending(self, user1, user2, when=None):
        """ Ajouter une demande vers un utilisateur """
        return user1.friends.add_sent(user2, when=when)

    def add_friends(self, user1, user2, when=None):
        """ Assigner deux utilisateurs comme amis """
        user1.friends.add_friend(user2, when=when)


class FriendList(DataModel):
    """ Liste d'amis """

    # Constantes
    DATA_KEYS = ['friends', 'received', 'sent']  # amis, demandes reçues, demandes envoyées
    ACTION_LABELS = {(True, False): _("Friend"), (False, True): _("Cancel request"), (False, False): _("Add to friends")}

    # Champs
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='friends', verbose_name=_("User"))
    objects = FriendListManager()

    # Getter
    def get_friend_ids(self):
        """ Renvoyer les ids des amis """
        return self.get_data('friends', {}).keys()

    def get_received_ids(self):
        """ Renvoyer les ids des demandeurs en attente """
        return self.get_data('received', {}).keys()

    def get_sent_ids(self):
        """ Renvoyer les ids des utilisateurs sollicités """
        return self.get_data('sent', {}).keys()

    def is_friend(self, user):
        """ Renvoyer si un utilisateur est un ami """
        return getattr(user, 'pk', user) in self.get_friend_ids()

    def is_received(self, user):
        """ Renvoyer si un utilisateur attend une validation """
        return getattr(user, 'pk', user) in self.get_received_ids()

    def is_sent(self, user):
        """ Renvoyer si un utilisateur a reçu une requête """
        return getattr(user, 'pk', user) in self.get_sent_ids()

    def get_friend_users(self):
        """ Renvoyer les utilisateurs amis """
        return get_user_model().objects.filter(pk__in=self.get_friend_ids())

    def get_received_users(self):
        """ Renvoyer les utilisateurs en attente """
        return get_user_model().objects.filter(pk__in=self.get_received_ids())

    def get_sent_users(self):
        """ Renvoyer les utilisateurs sollicités """
        return get_user_model().objects.filter(pk__in=self.get_sent_ids())

    def get_friend_count(self):
        """ Renvoyer le nombre d'amis """
        return len(self.get_data('friends', {}))

    def get_received_count(self):
        """ Renvoyer le nombre d'utilisateurs en attente """
        return len(self.get_data('received', {}))

    def get_sent_count(self):
        """ Renvoyer le nombre d'utilisateurs sollicités """
        return len(self.get_data('sent', {}))

    def get_all_users(self):
        """ Renvoyer tous les utilisateurs, par catégorie """
        return {'friends': self.get_friend_users(), 'received': self.get_received_users(), 'sent': self.get_sent_users()}

    def get_mutual_friend_users(self, user, count=False):
        """ Renvoyer les amis en commun avec un utilisateur """
        self_ids = frozenset(self.get_friend_ids())
        user_ids = frozenset(user.friends.get_friend_ids())
        mutual_ids = list(self_ids.intersection(user_ids))
        return len(mutual_ids) if count is True else get_user_model().objects.filter(pk__in=mutual_ids)

    def get_distinct_friend_users(self, user, symmetric=False, count=False):
        """
        Renvoyer les amis non communs avec un utilisateur

        :param count: si True, renvoyer le nombre d'éléments, ou sinon les éléments eux-mêmes
        :param user: utilisateur pour lequel on veut comparer la liste d'amis
        :param symmetric: définit si le calcul doit être symétrique.
        Lorsque symetric est False, on renvoie les amis de l'utilisateur courant
        qui ne sont pas amis avec user. Les amis de user qui ne sont pas amis avec l'utilisateur
        courant ne sont pas renvoyés. (= amis(a) ∖ amis(b), ce n'est pas un antislash mais l'opérateur)
        de différence entre deux enesembles
        Si symmetric est True, on affiche les utilisateurs des deux listes
        d'amis qui sont présents dans une seule des deux listes (renvoie plus d'entrées)
        (= amis(a) ∆ amis(b))
        """
        self_ids = set(self.get_friend_ids())
        user_ids = set(user.friends.get_friend_ids())
        distinct_ids = list(self_ids.symmetric_difference(user_ids)) if symmetric else list(self_ids.difference(user_ids))
        return len(distinct_ids) if count is True else get_user_model().objects.filter(pk__in=distinct_ids)

    def get_random_unknown_friend_users(self, count=10):
        """ Renvoyer une liste au hasard d'utilisateurs amis d'amis mais pas amis """
        user = get_user_model().objects.get(id=choice(self.get_friend_ids()))
        users = self.get_distinct_friend_users(user, False).order_by('?')[:count]
        return users

    def get_action_label(self, user):
        """
        Renvoyer le texte d'action par défaut par rapport au statut avec un utilisateur

        Si un utilisateur est déjà ami, renvoyer "Ami"
        Si une demande est en attente vers l'utilisateur, renvoyer "Annuler la demande"
        Si l'utilisateur est ni ami ni rien, renvoyer "Demander en ami"
        """
        status = (self.is_friend(user), user.friends.is_pending(self.user))
        return FriendList.ACTION_LABELS[status]

    def _get_active_friends(self):
        """ Générateur : Renvoyer la liste des amis avec des comptes encore actifs """
        friends = self.get_users()
        for friend in friends:
            if friend.can_login():
                yield friend

    # Propriétés
    active_friends = property(_get_active_friends)

    # Setter
    @transaction.atomic
    def add_friend(self, user, when=None):
        """ Ajouter un ami """
        if not self.is_friend(user) and user != self.user:
            now = when or timezone.now()
            friends = self.get_data('friends', {})
            friends[user.pk] = [now]
            self.set_data('friends', friends, save=True)
            user.friends.add_friend(self.user)
            self.remove_received(user)
            return True
        return False

    @transaction.atomic
    def add_received(self, user, when=None):
        """ Ajouter une demande reçue """
        if not self.is_received(user) and not self.is_friend(user) and user != self.user:
            now = when or timezone.now()
            received = self.get_data('received', {})
            received[user.pk] = [now]
            self.set_data('received', received, save=True)
            user.friends.add_sent(self.user)  # Par symétrie, ajouter un sent à l'autre utilisateur
            friend_pending_new.send(sender=user, recipient=self.user)
            return True
        return False

    @transaction.atomic
    def add_sent(self, user, when=None):
        """ Ajouter une demande envoyée """
        if not self.is_sent(user) and not self.is_friend(user) and user != self.user:
            now = when or timezone.now()
            sent = self.get_data('sent', {})
            sent[user.pk] = [now]
            self.set_data('sent', sent, save=True)
            user.friends.add_received(self.user)  # Par symétrie, ajouter un received à l'autre utilisateur
            friend_pending_new.send(sender=user, recipient=self.user)
            return True
        return False

    @transaction.atomic()
    def remove_friend(self, user):
        """ Supprimer un ami """
        if self.is_friend(user):
            friends = self.get_data('friends', {})
            del friends[user.pk]
            self.set_data('friends', friends, save=True)
            user.friends.remove_friend(self.user)
            return True
        return False

    @transaction.atomic()
    def remove_sent(self, user):
        """ Supprimer une demande envoyée """
        if self.is_sent(user):
            sent = self.get_data('sent', {})
            del sent[user.pk]
            self.set_data('sent', sent, save=True)
            user.friends.remove_received(self.user)
            return True
        return False

    @transaction.atomic()
    def remove_received(self, user):
        """ Supprimer une demande reçue """
        if self.is_received(user):
            received = self.get_data('received', {})
            del received[user.pk]
            self.set_data('received', received, save=True)
            user.friends.remove_sent(self.user)
            return True
        return False

    @transaction.atomic()
    def accept_received(self, user):
        """ Aceepter une demande reçue """
        if self.remove_received(user):
            self.add_friend(user)
            friend_accepted.send(sender=user, recipient=self.user)

    @transaction.atomic()
    def deny_received(self, user):
        """ Refuser une demande reçue """
        if self.remove_received(user):
            friend_denied.send(sender=user, recipient=self.user)

    def auto_action(self, user):
        """ Automatiquement envoyer ou annuler une demande à un utilisateur """
        if not self.is_friend(user):
            if self.is_sent(user):
                self.remove_sent(user)
            else:
                self.add_sent(user)
        return self.get_action_label(user)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("Friendship status for {user}").format(user=self.user)

    def __init__(self, *args, **kwargs):
        """ Initialiser l'objet """
        super(FriendList, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("friend status")
        verbose_name_plural = _("friend statuses")
        app_label = 'social'
