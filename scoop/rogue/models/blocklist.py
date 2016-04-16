# coding: utf-8
from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr

DEFAULT_LIST = 'blacklist'


class BlocklistManager(SingleDeleteManager):
    """ Manager de listes de blocage """

    # Getter
    def get_by_user(self, user):
        """ Renvoyer l'objet blocklist pour un utilisateur """
        return self.get_or_create(user=user)[0] if user is not None else self.get_global()

    def get_global(self):
        """ Renvoyer l'objet blocklist global """
        blocklist, _ = self.get_or_create(user=None)
        return blocklist

    def is_safe(self, sender, recipients, name=None):
        """ Renvoyer si deux utilisateurs n'ont pas de blocklist entre eux """
        if sender.is_staff or getattr(sender, 'bot', False) or sender.has_perm('rogue.can_bypass_blocks'):
            return True
        if self.is_globally_listed(sender):
            return False
        recipients = recipients if isinstance(recipients, (list, tuple, models.QuerySet)) else [recipients]
        blocklists = self.filter(user__in=recipients)
        sender_blocks = sender.blocklist.get_data(name or 'blacklist') or []
        for recipient in recipients:
            if recipient.pk in sender_blocks:
                return False
        for blocklist in blocklists:
            items = blocklist.get_data(name or 'blacklist') or []
            if sender.pk in items:
                return False
        return True

    def exists(self, recipient, sender, name=None):
        """ Renvoyer s'il existe une blocklist créée par recipient vers sender """
        blocklist = self.get_by_user(recipient)
        return blocklist.is_listed(sender, name)

    def get_user_ids(self, user, name=None):
        """ Renvoyer les ids d'utilisateurs dans une blocklist de user """
        blocklist = self.get_by_user(user)
        return blocklist.get_ids(name)

    def users_listed_by(self, user, name=None):
        """ Renvoyer les utilisateurs dans une blocklist de user """
        from django.contrib.auth import get_user_model
        # Liste de blocage
        ids_listed = self.get_user_ids(user, name=name)
        return get_user_model().objects.filter(pk__in=ids_listed)

    def is_globally_listed(self, user, name=None):
        """ Renvoyer si un utilisateur est dans une blocklist globale """
        return self.exists(None, user, name=name)

    def exclude_users(self, queryset, user, name=None):
        """ Renvoyer un queryset ne contenant pas les utilisateurs d'une blocklist """
        if queryset.model.__name__ in {'User', 'Profile'}:
            return queryset.exclude(pk__in=self.get_user_ids(user, name))
        return queryset

    # Setter
    def add(self, recipient, sender, name=None):
        """ Ajouter un utilisateur dans une blocklist """
        blocklist = self.get_by_user(recipient)
        return blocklist.add(sender, name)

    def remove(self, recipient, sender, name=None):
        """ Retirer un utilisateur d'une blocklist """
        blocklist = self.get_by_user(recipient)
        return blocklist.remove(sender, name)

    def toggle(self, recipient, sender, name=None):
        """ Basculer le listage d'un utilisateur dans une blocklist """
        blocklist = self.get_by_user(recipient)
        return blocklist.toggle(sender, name)

    def clear(self, user, name=None):
        """ Réinitialiser une blocklist """
        blocklist = self.get_by_user(user)
        return blocklist.clear(name=name)


class Blocklist(DatetimeModel, DataModel):
    """ Blocklist """

    # Constantes
    DATA_KEYS = ['blacklist', 'hidelist']

    # Champs
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, null=True, related_name='blocklist', on_delete=models.CASCADE, verbose_name=_("Blocker"))
    objects = BlocklistManager()

    # Getter
    @addattr(short_description=pgettext_lazy('users', "Blacklisted"))
    def get_count(self, name=None):
        """ Renvoyer le nombre d'entrées dans une blocklist """
        return len(self.get_data(name or DEFAULT_LIST, []))

    def get_total_count(self):
        """ Renvoyer le nombre total d'entrées dans toutes les blocklists """
        return sum([self.get_count(name) for name in self.DATA_KEYS if 'list' in name])

    def get_ids(self, name=None):
        """ Renvoyer les ID d'utilisateurs d'une blocklist """
        return self.get_data(name or DEFAULT_LIST, {}).keys()

    def is_listed(self, sender, name=None):
        """ Renvoyer si un utilisateur est bloqué par une blocklist """
        return getattr(sender, 'pk', sender) in self.get_ids(name)

    def get_list_date(self, sender, name=None):
        """ Renvoyer la date de mise en blocklist d'un utilisateur """
        data = self.get_data(name or DEFAULT_LIST, {})
        if getattr(sender, 'pk', sender) in data:
            return data[getattr(sender, 'pk', sender)][0]
        return None

    # Setter
    def add(self, sender, name=None):
        """
        Ajouter un utilisateur à une blocklist

        Un utilisateur du staff ne peut pas être ajouté à une blocklist
        :type sender: scoop.user.models.User or int
        :param name: nom de la liste de blocage
        """
        if getattr(sender, 'pk', sender) not in self.get_ids(name) and not getattr(sender, 'is_staff', False):
            now = timezone.now()
            data = self.get_data(name or DEFAULT_LIST, {})
            data[getattr(sender, 'pk', sender)] = [now]
            self.set_data(name or DEFAULT_LIST, data)
            self.save()
            return True
        return False

    def remove(self, sender, name=None):
        """
        Retirer un utilisateur d'une blocklist

        :type sender: scoop.user.models.User or int
        :param name: nom de la liste de blocage
        """
        if getattr(sender, 'pk', sender) in self.get_ids(name):
            data = self.get_data(name or DEFAULT_LIST)
            del data[getattr(sender, 'pk', sender)]
            self.set_data(name or DEFAULT_LIST, data)
            self.save()
            return True
        return False

    def toggle(self, sender, name=None):
        """
        Basculer l'enrôlement d'un utilisateur à une blocklist

        :type sender: scoop.user.models.User or int
        :param name: nom de la liste de blocage
        """
        if self.is_listed(sender, name or DEFAULT_LIST):
            self.remove(sender, name or DEFAULT_LIST)
            return False
        else:
            self.add(sender, name or DEFAULT_LIST)
            return True

    def clear(self, name=None):
        """ Remettre une blocklist à zéro """
        self.set_data(name or DEFAULT_LIST, {}, save=True)
        return True

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.time = self.now()
        super(Blocklist, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("blocklists")
        verbose_name_plural = _("blocklists")
        permissions = [['can_bypass_block', "Can bypass blocks"]]
        app_label = "rogue"
