# coding: utf-8
import re

import IPy
from celery.contrib.methods import task
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django_countries import countries
from django_countries.fields import CountryField
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr
from scoop.rogue.util.ipblock import is_relay_node
from scoop.rogue.util.signals import user_has_ip_blocked


class IPBlockManager(SingleDeleteManager):
    """ Manager des blocages d'IP """

    # Getter
    def active(self):
        """ Renvoyer les filtres actifs """
        return self.filter(active=True)

    def is_blocked(self, ip):
        """
        Renvoyer si une IP est bloquée
        :type ip: scoop.user.access.models.IP
        """
        from scoop.location.models import Country
        # Ignorer les IPs protégées
        if ip.is_protected():
            return {'blocked': False, 'level': 0, 'type': 0}
        # Vérifier d'abord les attributs de l'IP
        if ip.is_blocked(check=False) or not Country.objects.is_safe(ip.country):
            return {'blocked': True, 'level': ip.harm or 3, 'type': 0}
        # Ne chercher les autorisations de reverse que si l'IP a un reverse
        if ip.has_reverse():
            for ipblock in self.filter(active=True, type=6):
                if re.search(ipblock.hostname, ip.reverse):
                    return {'blocked': False, 'level': 0, 'type': 0}
        # Ne chercher les autorisations de FAI que si l'IP a un ISP
        if ip.has_isp():
            allows = self.filter(isp__iexact=ip.isp, active=True, type=7)
            if allows.exists():
                return {'blocked': False, 'level': 0, 'type': 0}
        # Vérifier l'ip
        blocks = self.filter(ip1=ip.ip, type=0, active=True)
        if blocks.exists():
            block_item = blocks[0]
            return {'blocked': True, 'level': block_item.harm, 'type': block_item.category}
        # Vérifier que l'IP est dans une plage ou pas
        blocks = self.filter(ip1__lte=ip.ip, ip2__gte=ip.ip, type=1, active=True)
        if blocks.exists():
            return {'blocked': True, 'level': blocks[0].harm, 'type': blocks[0].category}
        # Vérifier ensuite que l'IP n'est pas un nœud TOR ou un proxy
        if is_relay_node(ip.string):
            return {'blocked': True, 'level': 3, 'type': 10}
        # Ne chercher les blocages de reverse que si l'IP a un reverse
        if ip.has_reverse():
            # Vérifier le reverse de l'enregistrement IP
            for ipblock in self.filter(active=True, type=2).only('hostname', 'harm', 'category'):
                if ipblock.hostname.lower() in ip.reverse.lower():
                    return {'blocked': True, 'level': ipblock.harm, 'type': ipblock.category}
            # Vérifier le reverse de l'enregistrement, avec exclusion
            for ipblock in self.filter(active=True, type=3).only('hostname', 'hostname_exclude', 'harm', 'category'):
                if ipblock.hostname.lower() in ip.reverse.lower() and not re.search(ipblock.hostname_exclude, ip.reverse):
                    return {'blocked': True, 'level': ipblock.harm, 'type': ipblock.category}
        # Ne chercher les blocages de FAI que si l'IP en a un
        if ip.has_isp():
            # Vérifier les ISP
            for ipblock in self.filter(isp__istartswith=ip.isp, active=True, type=4).only('hostname_exclude', 'harm', 'category'):
                if ipblock.hostname_exclude == '' or not re.search(ipblock.hostname_exclude, ip.reverse):
                    return {'blocked': True, 'level': ipblock.harm, 'type': ipblock.category}
        # Vérifier le pays
        if ip.has_country():
            blocks = self.filter(country_code__iexact=ip.country, active=True, type=5)
            if blocks.exists():
                return {'blocked': True, 'level': blocks[0].harm, 'type': blocks[0].category}
        # Aucun blocage trouvé
        return {'blocked': False, 'level': 0, 'type': 0}

    @task(ignore_result=True)
    def is_user_blocked(self, user):
        """ Renvoyer si l'utilisateur utilise une IP bloquée par un filtre """
        # Chemins rapides
        if user is None or user.is_superuser or user.is_staff:
            return False
        # Récupérer les IPs de l'utilisateur
        from scoop.user.access.models import IP
        # Parcourir les IPs, si une est bloquée, renvoyer Vrai
        ips = IP.objects.for_user(user).distinct()
        for ip in ips:
            status = self.is_blocked(ip)
            if status['blocked']:
                user_has_ip_blocked.send(user, ip=ip, harm=status['level'])
                return status
        return False

    def user_blocked_ips(self, user, value=True):
        """ Renvoyer la liste des IPs bloquées pour un utilisateur """
        if user is None or user.is_superuser or user.is_staff:
            return []
        # Récupérer les IPs de l'utilisateur
        from scoop.user.access.models import IP
        # Renvoyer seulement les IPs bloquées
        ips = IP.objects.for_user(user).distinct()
        return [ip for ip in ips if self.is_blocked(ip)['blocked'] is value]

    def blocked_users(self, block_criteria=None, user_criteria=None):
        """ Renvoyer les utilisateurs bloqués par les filtres """
        from scoop.user.models import User
        # Calculer les IP à bloquer
        blocked_ips, allowed_ips = set(), set()
        blocks = self.active().filter(type__lt=6, **(block_criteria or {}))
        allows = self.active().filter(type__gte=6, **(block_criteria or {}))
        for block in blocks:
            for ip in block.get_blocked_ip_set():
                blocked_ips.add(ip.id)
        for allow in allows:
            for ip in allow.get_allowed_ip_set():
                allowed_ips.add(ip.id)
        users = User.objects.filter(is_active=True, is_staff=False, userips__ip__id__in=list(blocked_ips - allowed_ips), **(user_criteria or {})).distinct()
        return users

    # Setter
    def expire(self):
        """ Faire expirer les filtres """
        return self.filter(active=True, expires__isnull=False, expires__lt=timezone.now()).update(active=False)

    def block_ips(self, ips, harm=3, category=0, description=None):
        """
        Bloquer une ou plusieurs adresse IP
        :param ips: id ou instance d'IP ou chaîne au format A.B.C.D
        :type ips: list | tuple | set | IP | str | int
        :returns: les nouveaux blocages d'IP
        """
        from scoop.user.access.models.ip import IP
        ips = make_iterable(ips)
        new_blocks = []
        for ip in ips:
            try:
                # Convertir en  une instance d'IP
                if isinstance(ip, str):
                    ip = IP.objects.get_by_ip(ip)
                elif isinstance(ip, int):
                    ip = IP.objects.get(id=ip)
                elif isinstance(ip, IP):
                    ip = ip
                else:
                    raise TypeError("IPs must be strings, ints or IPs.")
                if not ip.is_protected():
                    block, created = self.get_or_create(type=0, ip1=ip.ip, isp=ip.isp, harm=harm, category=category, description=description or "")
                    if created is False:
                        block.active = True
                        block.save()
                    else:
                        new_blocks.append(block)
            except TypeError:
                pass
            return new_blocks

    def block_ip_range(self, ip1, ip2, harm=2, category=0, description=None):
        """
        Bloquer une plage d'adresses IP
        :type ip1: int
        :type ip2: int
        """
        try:
            from scoop.user.access.models.ip import IP
            # Vérifier que la plage est correcte
            if IP.get_ip_value(ip1) > IP.get_ip_value(ip2):
                ip1, ip2 = ip2, ip1  # inverser la plage si à l'envers
            if ip1 != ip2:  # bloquer une simple ip si les deux ip sont identiques
                self.create(type=1, ip1=IP.get_ip_value(ip1), ip2=IP.get_ip_value(ip2), harm=harm, category=category, description=description or "")
            else:
                self.block_ips(ip1, harm=harm)
        except IPBlock.DoesNotExist:
            pass

    def block_user(self, user, harm=3, category=0, description=None):
        """ Bloquer les adresses IP d'un utilisateur """
        from scoop.user.access.models import IP
        # Bloquer les IPs de l'utiliaateur
        ips = IP.objects.for_user(user).values_list('string', flat=True)
        self.block_ips(ips, harm, category=category, description=description)

    def block_reverse(self, name, exclude=None, harm=2, category=0, description=None):
        """ Bloquer un reverse (regex) """
        criteria = {'type': 3 if exclude else 2, 'hostname': name, 'harm': harm, 'category': category, 'description': description or ""}
        criteria.update({'hostname_exclude': exclude} if exclude else {})
        new_block, created = self.get_or_create(**criteria)
        return new_block if created else False

    def block_country_code(self, code, harm=3):
        """ Bloquer toutes les IP d'un pays """
        code = code.strip().upper()
        if code in countries.OFFICIAL_COUNTRIES:
            self.create(type=5, country_code=code, harm=harm)


class IPBlock(DatetimeModel):
    """
    Régle de blocage d'IP
    Les régles d'autorisation (types 6 et 7) sont prioritaires sur les
    règles de blocage.
    """
    # Constantes
    TYPES = [[0, _("Single address")], [1, _("Address range")], [2, _("Partial host")], [3, _("Partial host with exclusion")], [4, _("ISP with host exclusion")], [5, _("Country code")],
             [6, _("Allowed host")], [7, _("Allowed ISP")]]
    CATEGORIES = [[0, _("General")], [1, _("Proxy")], [2, _("Server")], [3, _("Compromised IP")], [4, _("Repeated trouble")], [10, _("Tor network")], [11, _("Anonymous network")],
                  [12, _("VPN")]]
    HARM = [[1, _("Rarely harmful")], [2, _("Often harmful")], [3, _("Always harmful")]]
    # Champs
    active = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('ipblocking', "Active"))
    expires = models.DateTimeField(default=None, blank=True, null=True, verbose_name=_("Expires"))
    type = models.SmallIntegerField(choices=TYPES, default=0, db_index=True, verbose_name=_("Type"))
    category = models.SmallIntegerField(choices=CATEGORIES, default=0, db_index=True, verbose_name=_("Category"))
    description = models.TextField(default="", blank=True, verbose_name=_("Description"))
    harm = models.SmallIntegerField(choices=HARM, default=2, validators=[MaxValueValidator(4)], verbose_name=_("Harm level"))
    country_code = CountryField(blank=True, verbose_name=_("Country"))
    isp = models.CharField(max_length=64, blank=True, verbose_name=_("ISP"))
    hostname = models.CharField(max_length=48, blank=True, default='', verbose_name=_("Host name"))
    hostname_exclude = models.CharField(max_length=48, default='', blank=True, verbose_name=_("Exclude host name"))  # regex
    ip1 = models.DecimalField(max_digits=39, decimal_places=0, default=0, db_index=True, verbose_name=_("IP 1"))
    ip2 = models.DecimalField(max_digits=39, decimal_places=0, default=0, db_index=True, verbose_name=_("IP 2"))
    representation = models.CharField(max_length=128, blank=False, verbose_name=_("Blocking representation"))
    objects = IPBlockManager()

    # Getter
    def get_blocked_ip_set(self):
        """ Renvoyer les adresses IP bloquées par ce seul filtre """
        from scoop.user.access.models import IP
        # Renvoyer pour une IP simple
        if self.type == 0:
            return IP.objects.filter(ip=self.ip1)
        # Renvoyer pour une plage d'IP
        elif self.type == 1:
            return IP.objects.filter(ip__range=(self.ip1, self.ip2))
        # Renvoyer pour le nom d'hôte
        elif self.type == 2 and self.hostname:
            return IP.objects.filter(reverse__icontains=self.hostname)
        # Renvoyer pour le nom d'hôte avec exclusion
        elif self.type == 3 and self.hostname:
            return IP.objects.filter(reverse__icontains=self.hostname).exclude(**({'reverse__iregex': self.hostname_exclude} if self.hostname_exclude else {}))
        # Renvoyer pour le nom de FAI avec exclusion
        elif self.type == 4:
            items = IP.objects.filter(isp__istartswith=self.isp)
            if self.hostname_exclude != "":
                items = items.exclude(reverse__iregex=self.hostname_exclude)
            return items
        # Renvoyer pour le pays
        elif self.type == 5:
            return IP.objects.filter(country=self.country_code)
        # Renvoyer 0 pour un mode Allowed
        else:
            return IP.objects.none()

    def get_allowed_ip_set(self):
        """ Renvoyer les adresses IP en liste blanche pour ce filtre """
        from scoop.user.access.models import IP
        # Nom d'hôte
        if self.type == 6:
            return IP.objects.filter(reverse__iregex=self.hostname)
        # FAI
        elif self.type == 7:
            return IP.objects.filter(isp=self.isp)
        else:
            return IP.objects.none()

    @addattr(short_description=_("IP count"))
    def get_blocked_ip_count(self):
        """ Renvoyer le nombre d'IP bloquées par ce filtre """
        return self.get_blocked_ip_set().count()

    @addattr(short_description=_("IP count"))
    def get_allowed_ip_count(self):
        """ Renvoyer le nombre d'IP en liste blanche via ce filtre """
        return self.get_allowed_ip_set().count()

    # Setter
    @transaction.atomic
    def block_ip_set(self):
        """ Marquer les IPs concernées par le filtre comme bloquées """
        for ip in self.get_blocked_ip_set():
            ip.block()

    @transaction.atomic
    def unblock_ip_set(self):
        """ Marquer les IPs concernées par le filtre comme non bloquées """
        for ip in self.get_allowed_ip_set():
            ip.block(blocked=False, harm=0)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.hostname = self.hostname.strip()
        self.hostname_exclude = self.hostname_exclude.strip()
        self.country_code = self.country_code
        self.representation = self.__str__()
        super(IPBlock, self).save(*args, **kwargs)

    def clean(self):
        # Valider l'état de l'objet
        if self.type == 0 and self.ip1 == 0:
            raise ValidationError(_("A single IP block must have a valid IP to block."))
        elif self.type == 1 and ((self.ip1 == 0 or self.ip2 == 0) or (self.ip2 <= self.ip1)):
            raise ValidationError(_("A range IP block must have valid IPs to block."))
        elif self.type in {2, 3} and self.hostname == '':
            raise ValidationError(_("A hostname block must have a partial hostname to block."))
        elif self.type == 4 and self.isp == '':
            raise ValidationError(_("An ISP block must have a valid ISP name to block."))
        elif self.type == 5 and self.country_code == '':
            raise ValidationError(_("A country block must have a valid country code to block."))
        elif self.type == 6 and self.hostname == '':
            raise ValidationError(_("A hostname permission must have a valid hostname."))
        elif self.type == 7 and self.isp == '':
            raise ValidationError(_("An ISP permission must have a valid ISP."))
        else:
            raise ValidationError(_("This rule type {number} is unknown.").format(number=self.type))

    def __str__(self):
        """ Renvoyer une représentation unicode du filtre """
        if self.type == 0:
            return _("Blocking of {ip}").format(ip=IPy.IP(str(self.ip1)))
        elif self.type == 1:
            return _("Blocking of IPs from {ip1} to {ip2}").format(ip1=IPy.IP(str(self.ip1)), ip2=IPy.IP(str(self.ip2)))
        elif self.type == 2:
            return _("Blocking of reverse {reverse}").format(reverse=self.hostname)
        elif self.type == 3:
            return _("Blocking of reverse {reverse} but not with {exclude}").format(reverse=self.hostname, exclude=self.hostname_exclude)
        elif self.type == 4:
            return _("Blocking of ISP {isp}").format(isp=self.isp) if self.hostname_exclude == "" else _("Blocking of ISP {isp} minus {exclude}").format(isp=self.isp,
                                                                                                                                                         exclude=self.hostname_exclude)
        elif self.type == 5:
            return _("Blocking of country with code {code}").format(code=self.country_code)
        elif self.type == 6:
            return _("Authorization of reverse {reverse}").format(reverse=self.hostname)
        elif self.type == 7:
            return _("Authorization of ISP {isp}").format(isp=self.isp)

    # Métadonnées
    class Meta:
        verbose_name = _("IP blocking")
        verbose_name_plural = _("IP blocking")
        unique_together = (('type', 'ip1', 'ip2', 'isp', 'hostname', 'country_code'),)
        index_together = [['ip1', 'ip2']]
        app_label = 'rogue'
