# coding: utf-8
import logging
import re
from datetime import datetime

import IPy
from django.apps.registry import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.manager import GeoManager
from django.core.urlresolvers import reverse_lazy
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.backends.dummy.base import IntegrityError
from django.db.models.aggregates import Count
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django_countries.data import COUNTRIES
from pygeoip import GeoIP

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.core.util.shortcuts import addattr
from scoop.location.util.country import get_country_icon_html
from scoop.user.access.util.access import STATUS_CHOICES, reverse_lookup


logger = logging.getLogger(__name__)


class IPManager(GeoManager):
    """ Manager des IP """

    # Getter
    def get_by_natural_key(self, ip):
        """ Renvoyer une IP par clé naturelle """
        return self.get(ip=ip)

    def get_by_ip(self, ip_string):
        """ Renvoyer l'objet IP depuis une chaîne """
        try:
            return self.get(ip=IP.get_ip_value(ip_string))
        except IP.DoesNotExist:
            try:
                new_ip = IP()
                new_ip.set_ip_address(ip_string, save=True)
                return new_ip
            except IntegrityError:
                return None

    def get_localhost(self):
        """ Renvoyer l'objet IP pour localhost """
        return self.get_by_ip('127.0.0.1')

    def get_by_request(self, request):
        """ Renvoyer l'objet IP pour un objet Request """
        if request is not None:
            return self.get_by_ip(request.get_ip())
        else:
            return None

    def for_user(self, user):
        """ Renvoyer les IPs d'un utilisateur """
        return self.filter(userip__user=user)

    def get_for_user_count(self, user):
        """ Renvoyer le nombre d'IP utilisées par un utilisateur """
        return self.for_user(user).count()

    def get_country_codes(self):
        """ Renvoyer la liste de codes pays des """
        return self.exclude(country="").values('country').annotate(count=Count('country')).distinct().order_by('-count')

    def __init__(self, *args, **kwargs):
        """ Initialiser le manager """
        super(IPManager, self).__init__(*args, **kwargs)
        # Initialiser l'outil GeoIP dans le manager
        if not hasattr(self, 'geoip'):
            try:
                self.geoip = GeoIP(settings.GEOIP_PATH)
                self.geoisp = GeoIP(settings.GEOISP_PATH)
            except AttributeError:
                pass


class IP(DatetimeModel, CoordinatesModel):
    """ Adresse IP """

    # Constantes
    HARMFUL_LEVEL = 2
    PROTECTED_IPS = [r'^127\.', r'^192\.168\.'] + list(getattr(settings, 'INTERNAL_IPS', []))

    # Champs
    ip = models.DecimalField(null=False, blank=True, unique=True, max_digits=39, decimal_places=0, db_index=True, verbose_name=_("Decimal"))
    string = models.CharField(max_length=48, verbose_name=_("String"))
    reverse = models.CharField(max_length=80, blank=True, verbose_name=_("Reverse"))  # état de résolution du reverse
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES, verbose_name=_("Reverse status"))
    isp = models.CharField(max_length=64, blank=True, verbose_name=_("ISP"))
    country = models.CharField(max_length=2, blank=True, choices=COUNTRIES.items(), db_index=True, verbose_name=_("Country"))
    harm = models.SmallIntegerField(default=0, db_index=True, validators=[MinValueValidator(0), MaxValueValidator(4)], verbose_name=_("Harm"))
    blocked = models.BooleanField(default=False, db_index=True, verbose_name=_("Blocked"))
    updated = models.DateTimeField(default=datetime(1970, 1, 1), verbose_name=pgettext_lazy('ip', "Updated"))
    dynamic = models.NullBooleanField(default=None, verbose_name=_("Dynamic"))  # IP dynamique ?
    city_name = models.CharField(max_length=96, blank=True, verbose_name=_("City name"))
    objects = IPManager()

    # Getter
    def natural_key(self):
        """ Renvoyer une IP par sa clé naturelle """
        return 'ip',

    def get_ip_address(self):
        """ Renvoyer la chaîne d'adresse de l'IP """
        return self.string or IPy.IP(int(self.ip)).strNormal()

    @addattr(short_description=_("Class"))
    def get_ip_class(self):
        """ Renvoyer la classe de l'IP, de A à E """
        value = int(self.ip)
        if value & (0b1 << 31) == 0:  # 0.0.0.0 à 127.255.255.255
            return "A"
        elif value & (0b10 << 30) == (0b10 << 30):  # 128.0.0.0 à 191.255.255.255
            return "B"
        elif value & (0b110 << 29) == (0b110 << 29):  # 192.0.0.0 à 223.255.255.255
            return "C"
        elif value & (0b1110 << 28) == (0b1110 << 28):  # 224.0.0.0 à 239.255.255.255
            return "D"
        elif value & (0b1111 << 28) == (0b1111 << 28):  # 240.0.0.0 à 255.255.255.255
            return "E"

    def get_geoip(self):
        """ Renvoyer les informations de localisation de l'IP """
        try:
            return IP.objects.geoip.record_by_addr(self.string) or {}
        except Exception as e:
            logger.warning(e)
            return {'country_code': '', 'latitude': 0.0, 'longitude': 0.0}

    @addattr(short_description=_("Country"))
    def get_country_code(self):
        """ Renvoyer le code pays de l'IP """
        code = self.get_geoip().get('country_code', "").upper()
        return code

    @addattr(short_description=_("Country"))
    def get_country(self):
        """ Renvoyer l'instance Country pour l'IP """
        if not apps.is_installed('scoop.location'):
            return None
        from scoop.location.models import Country
        # Renvoyer le pays correspondant au code, ou aucun si A1, A2 etc.
        return Country.objects.get_by_code2_or_none(self.country)

    @addattr(short_description=_("Country"))
    def get_country_name(self):
        """ Renvoyer le nom du pays de l'IP """
        return self.get_country_display()

    def get_closest_city(self):
        """ Renvoyer l'instance de City la plus proche des coordonnées GPS de l'adresse IP '"""
        if not apps.is_installed('scoop.location'):
            return None
        try:
            from scoop.location.models import City
            if self.string in settings.INTERNAL_IPS:
                return IP.objects.get_by_ip(settings.PUBLIC_IP).get_closest_city()
            # Trouver la ville la plus proche des coordonnées GPS de l'IP, portant idéalement un nom
            geoip = self.get_geoip() or dict()
            if geoip.get('latitude', 0) != 0:
                point, name = [geoip['latitude'], geoip['longitude']], geoip['city']
                return City.objects.find_by_name(point, name=name)
            return None
        except Exception:
            return None

    @addattr(short_description=_("ISP"))
    def get_isp(self):
        """ Renvoyer les informations du FAI de l'IP """
        org = IP.objects.geoisp.org_by_addr(self.ip_address) or ""
        return org

    @addattr(short_description=_("City name"))
    def get_city_name(self):
        """ Renvoyer le nom de la ville de l'IP """
        return self.city_name or _("N/D")

    @addattr(short_description=_("Reverse"))
    def get_reverse(self, force_lookup=False):
        """ Renvoyer le nom inversé de l'IP """
        if force_lookup is True:
            return reverse_lookup(self.get_ip_address())
        return self.reverse or reverse_lookup(self.get_ip_address())

    @addattr(short_description=_("Short reverse"))
    def get_short_reverse(self):
        """ Renvoyer un nom inversé court pour l'IP """
        reverse = self.reverse
        shorter = re.sub('\d', '', reverse)
        shorter = re.sub('\W{2,8}', '-', shorter)
        shorter = re.sub('(\W$|^\W)', '', shorter)
        return shorter

    @staticmethod
    def get_ip_value(ip_string):
        """
        Renvoyer la valeur décimale d'une IP

        :param ip_string: chaîne de l'IP, de type A.B.C.D ou 128bits)
        """
        try:
            return IPy.IP(ip_string).ip
        except ValueError:
            return 0

    @addattr(admin_order_field='ip', short_description=_("Hexadecimal"))
    def get_hex(self, group=2):
        """ Renvoyer la représentation hexadécimale de l'IP """
        if group is not int(group) or not group > 0:
            group = 1
        result = "{:X}".format(int(self.ip))
        output = "".join([digit + ':' if idx % group == group - 1 and idx < len(result) - 1 else digit for idx, digit in enumerate(result)])
        return output

    @addattr(short_description=_("Users"))
    def get_users(self):
        """ Renvoyer les utilisateurs ayant navigué avec cette IP """
        users = get_user_model().objects.filter(userips__ip=self).order_by('-pk')
        return users

    @addattr(short_description=_("Number of users"))
    def get_user_count(self):
        """ Renvoyer le nombre d'utilisateurs ayant navigué avec cette IP """
        return self.get_users().count()

    def get_subnet_range(self, bits=24):
        """
        Renvoyer la plage d'IP (long) du sous réseau de l'IP

        :param bits: taille du masque, en bits
        """
        keep = 32 - bits
        mask_subnet = (1 << keep) - 1
        mask_network = ~mask_subnet
        network = int(self.ip) & mask_network
        network_end = network | mask_subnet
        return [network, network_end]

    def get_subnet_ips(self, bits=24):
        """ Renvoyer les IP du sous-réseau de l'IP, avec un masque de n bits """
        iprange = self.get_subnet_range(bits)
        # Renvoyer les résultats entre network et network_end
        ips = IP.objects.filter(ip__range=(iprange[0], iprange[1]))
        return ips

    def get_subnet_users(self, bits=24):
        """ Renvoyer les utilisateurs ayant une IP du sous-réseau """
        iprange = self.get_subnet_range(bits)
        users = get_user_model().objects.filter(userip__ip__ip__range=(iprange[0], iprange[1])).distinct()
        return users

    def has_reverse(self):
        """ Renvoyer si l'IP possède un nom inversé """
        if ('in-addr.arpa' in self.reverse) or '.' not in self.reverse:
            return False
        return True

    def has_isp(self):
        """ Renvoyer si l'IP possède un FAI """
        return self.isp.strip() != ""

    def has_country(self):
        """ Renvoyer si l'IP possède un pays """
        return self.country.strip() != ""

    def get_blocked_status(self, check=False):
        """
        Renvoyer les informations de blocage de l'IP
        :param check: Recalculer l'état de blocage de l'IP
        """
        if check is True:
            from scoop.rogue.models import IPBlock
            # Vérifier complètement si l'IP est dangereuse et bloquée
            return IPBlock.objects.is_blocked(self)
        return {'blocked': self.blocked, 'harm': self.harm}

    def is_blocked(self, check=False):
        """
        Renvoyer si l'IP est bloquée
        :param check: Recalculer l'état de blocage de l'IP
        """
        result = self.get_blocked_status(check)
        return result['blocked']

    def is_harmful(self):
        """ Renvoyer si l'adresse IP est dangereuse """
        return self.harm >= IP.HARMFUL_LEVEL

    def is_protected(self):
        """ Renvoyer si l'IP est spéciale et protégée """
        for regex in self.PROTECTED_IPS:
            if re.search(regex, self.string):
                return True
        return False

    @staticmethod
    def is_country_harmful(code):
        """ Renvoyer si un code pays est dangereux """
        if not code or code.lower() in getattr(settings, 'LOCATION_SAFE_COUNTRIES', code.lower()):
            return False
        return True

    @addattr(allow_tags=True, short_description=_("Icon"))
    def get_country_icon(self):
        """ Renvoyer le HTML du drapeau du pays de l'IP """
        if self.has_country():
            return get_country_icon_html(self.country, self.get_country_name())

    # Setter
    def set_ip_address(self, ip_string, force_lookup=False, save=False):
        """
        Définir l'adresse IP de l'objet

        :param ip_string: chaîne du type A.B.C.D
        :param force_lookup: forcer le lookup DNS même si l'instance IP possède déjà des informations
        :param save: Enregistrer l'IP directement après
        """
        try:
            self.ip = IP.get_ip_value(ip_string)
            self.string = str(ip_string)
            reverse_status = self.get_reverse(force_lookup=force_lookup)
            if isinstance(reverse_status, dict):
                self.reverse = str(reverse_status['name'])
                self.status = reverse_status['status']
            else:
                self.reverse = reverse_status
            self.isp = self.get_isp()[0:64]
            self.country = self.get_country_code()
            self.harm = 3 * IP.is_country_harmful(self.country)  # 3 si True, 0 sinon
            geoip_info = self.get_geoip() or {'latitude': 0, 'longitude': 0, 'city': ''}
            self.latitude = geoip_info['latitude']
            self.longitude = geoip_info['longitude']
            self.city_name = geoip_info['city'] or ""
            self.updated = timezone.now()
            # Sauvegarder si demandé
            if save:
                self.save(force_update=self.id is not None)
        except Exception as e:
            logger.warning(e)
        return self

    def block(self, blocked=True, harm=3, save=False):
        """ Bloquer l'IP """
        self.harm = harm
        self.blocked = blocked
        if save is True:
            self.save()

    def check_blocked(self, force=False):
        """ Vérifier et renvoyer si l'IP est potentiellement dangereuse """
        from scoop.rogue.models import IPBlock
        from scoop.rogue.util.signals import ip_blocked
        # Vérifier via IPBlock si l'IP doit être bloquée
        if not self.blocked or force:
            status = IPBlock.objects.is_blocked(self)
            if status['blocked'] is True:
                self.block(status['blocked'], status['level'], save=False)
                ip_blocked.send(sender=self, harm=status['level'])
                return True
        return False

    # Propriétés
    ip_address = property(get_ip_address, set_ip_address)
    geoip = property(get_geoip)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "{}".format(self.ip_address)

    def __repr__(self):
        """ Renvoyer la représentation ASCII de l'objet """
        return "@{}".format(self.ip_address)

    def get_absolute_url(self):
        """ Renvoyer l'URL de la page de l'objet """
        return reverse_lazy('access:ip-view', args=[self.id])

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        force_lookup = kwargs.pop('force_lookup', False)
        self.set_ip_address(self.string, force_lookup=force_lookup, save=False)
        super(IP, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = "IP"
        verbose_name_plural = "IP"
        app_label = 'access'
