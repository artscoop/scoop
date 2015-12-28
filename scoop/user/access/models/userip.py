# coding: utf-8
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.user.ippoint import IPPointModel
from scoop.core.util.data.dateutil import now
from scoop.user.util.signals import userip_created
from unidecode import unidecode


class UserIPManager(models.Manager):
    """ Manager des IPs des utilisateurs """

    # Getter
    def countries_for(self, user, as_codes=True, days=None):
        """ Renvoyer les instances de pays d'IP pour l'utilisateur """
        criteria = {} if days is None else {'time__gt': now() - 86400 * days}
        country_list = set(self.filter(user=user, **criteria).exclude(ip__country='').values_list('ip__country', flat=True))
        if not as_codes:
            from scoop.location.models import Country
            # Liste d'objets Country
            country_list = Country.objects.filter(code2__in=country_list)
        return country_list

    def for_user(self, user):
        """ Renvoyer les UserIP pour un utilisateur """
        return self.filter(user=user)

    def related_users(self, user, exclude_self=False, harmful=False):
        """
        Renvoyer les utilisateurs partageant des IP avec un utilisateur
        :type user: scoop.models.user.User | django.auth.models.User
        """
        exclude_criteria = {'pk': user.pk} if exclude_self is True else {}
        criteria = {'ip__harm__gt': 0} if harmful else {}  # Récupérer ceux qui utilisent les mêmes IP dangereuses
        ip_ids = self.filter(user=user).values_list('ip__id', flat=True)
        users = get_user_model().objects.filter(userips__ip__id__in=ip_ids, **criteria).exclude(**exclude_criteria).order_by('-id').distinct()
        return users

    def get_city_for(self, user):
        """ Renvoyer l'instance City la plus appropriée pour une des IPs de l'utilisateur """
        userips = self.for_user(user)
        if userips.exists():
            userip = userips[0]
            city = userip.ip.get_closest_city()
            return city
        return None

    def city_names_for(self, user):
        """ Renvoyer les noms de villes des IPs d'un utilisateur """
        return {userip.ip.get_city_name() for userip in self.for_user(user).iterator()} if user else {}

    # Setter
    def set(self, user, ip):
        """ Enregistrer une nouvelle IP pour un utilisateur """
        if user and user.is_authenticated() and ip:
            if self.filter(user=user, ip=ip).update(time=now()) == 0:
                userip = self.create(user=user, ip=ip)
                userip_created.send(userip)
                return userip
            else:
                return self.get(user=user, ip=ip)


class UserIP(IPPointModel, DatetimeModel):
    """ IP d'un utilisateur """
    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='userips', verbose_name=_("User"))
    objects = UserIPManager()

    # Getter
    def related_users(self):
        """ Renvoyer les utilisateurs partageant les mêmes IP que l'utilisateur """
        return UserIP.objects.related_users(self.user)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{user}@{ip}").format(user=self.user, ip=self.get_ip())

    def __repr__(self):
        """ Renvoyer la représentation texte de l'objet """
        return unidecode(self.__str__())

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(UserIP, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("user IP")
        verbose_name_plural = _("user IPs")
        unique_together = (('ip', 'user'),)
        app_label = 'access'
