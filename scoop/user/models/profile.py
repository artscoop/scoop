# coding: utf-8
import hashlib
import logging
import os
import urllib

from annoying.fields import AutoOneToOneField
from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models.manager import Manager
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.birth import BirthManager, BirthModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.namedfilter import NamedFilterManager
from scoop.core.abstract.social.like import LikableModel
from scoop.core.util.data.dateutil import is_new
from scoop.core.util.django.apps import is_installed
from scoop.core.util.model.model import SingleDeleteQuerySetMixin
from scoop.core.util.shortcuts import addattr
from scoop.user.util.signals import check_stale, check_unused, profile_banned, profile_picture_changed


logger = logging.getLogger(__name__)


class ProfileQuerySetMixin(object):
    """ Mixin de queryset de profils """

    # Getter
    def verified(self):
        """ Renvoyer les profils vérifiés uniquement """
        return self.filter(harmful=False)

    def get_by_uuid(self, uuid):
        """ Renvoyer un profil dont l'utilisateur possède un UUID """
        return self.get(user__uuid=uuid)


class ProfileQuerySet(models.QuerySet, SingleDeleteQuerySetMixin, ProfileQuerySetMixin):
    """ Queryset des profils """
    pass


class BaseProfileManager(Manager.from_queryset(ProfileQuerySet), BirthManager, NamedFilterManager, ProfileQuerySetMixin):
    """ Manager de base de profils """

    def get_queryset(self):
        """ Renvoyer le queryset par défaut du manager """
        return super(BaseProfileManager, self).get_queryset().filter(user__deleted=False)

    # Getter
    def active(self):
        """ Renvoyer les profils actifs """
        return self.filter(user__bot=False, user__is_active=True)


class BaseProfile(BirthModel, LikableModel, PicturableModel, DataModel):
    """ Profil de base """

    # Constantes
    GENDER = [[0, _("Male")], [1, _("Female")], [2, _("Other")]]
    MALE, FEMALE, GENDER_OTHER = 0, 1, 2
    NULLABLE_GENDER = [['', pgettext_lazy('gender', "All")]] + GENDER
    CACHE_KEY = {'online': 'user.profile.online.%d', 'online.set': 'user.profile.online.set', 'online.count': 'user.profile.online.count',
                 'logout.force': 'user.profile.logout.%d'}
    DATA_KEYS = {'baninfo', 'admin', 'deactivation', 'logins'}

    # Champs
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, related_name='profile', primary_key=True, on_delete=models.PROTECT, verbose_name=_("User"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('profile', "Updated"))
    gender = models.SmallIntegerField(null=False, blank=False, choices=GENDER, default=0, db_index=True, verbose_name=_("Gender"))
    picture = models.ForeignKey('content.Picture', null=True, blank=True, on_delete=models.SET_NULL, help_text=_("Main profile picture"),
                                related_name='+', verbose_name=_("Picture"))
    banned = models.BooleanField(default=False, verbose_name=pgettext_lazy('profile', "Banned"))
    harmful = models.NullBooleanField(default=None, verbose_name=pgettext_lazy('profile', "Harmful"))
    if apps.is_installed('scoop.location'):
        city = models.ForeignKey('location.City', null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="+", verbose_name=_("City"))

    # Getter
    @addattr(boolean=True, admin_order_field='user__date_joined', short_description=_("New"))
    def is_new(self, days=7):
        """ Renvoyer si le profil est récent """
        return is_new(self.user.date_joined, days)

    def get_access_log(self, since=None):
        """
        Renvoyer les accès de l'utilisateur

        :param since: secondes, timedelta ou datetime
        """
        if is_installed('scoop.user.access'):
            from scoop.user.access.models import Access
            # Renvoyer les accès depuis une certaine date ou tous
            items = Access.objects.by_user(self.user, limit=None)
            if since is not None:
                return items.filter(time__gt=Access.since(since))
            return items
        return []

    def get_ips(self, as_ips=False):
        """ Renvoyer les IPs du profil """
        if is_installed('scoop.user.access'):
            from scoop.user.access.models import UserIP, IP
            # Renvoyer des UserIP ou des IP
            if as_ips is False:
                return UserIP.objects.for_user(self.user)
            return IP.objects.for_user(self.user)
        return []

    def is_banned(self):
        """ Renvoyer si le profil est banni """
        return self.banned

    def is_verified(self):
        """ Renvoyer si le profil a été vérifié et non dangereux """
        return self.harmful is False

    def is_bannable(self):
        """ Renvoyer si le profil peut être banni """
        return not (self.user.is_superuser or self.user.is_staff)

    def get_picture(self, request, use_default=True):
        """ Renvoyer l'image principale du profil """
        # Renvoyer l'image si elle est définie
        if self.picture is not None:
            if (request and request.user.is_staff) or self.picture.moderated:
                return self.picture
        # Choisir le nom de fichier par défaut
        if use_default is True:
            if not hasattr(settings, 'USER_DEFAULT_PICTURE_PATH'):
                logging.warning(_("No default path for user pictures. Add a directory path relative to MEDIA_URL in settings.USER_DEFAULT_PICTURE_PATH"))
            else:
                filename = getattr(settings, 'USER_DEFAULT_PICTURE_NAME', 'user-{0.gender}.jpg').format(self)
                fullpath = os.path.join(settings.USER_DEFAULT_PICTURE_PATH, filename)
                return fullpath
        return ''

    def get_pictures(self, *args, **kwargs):
        """ Renvoyer toutes les images du profil sans l'image principale """
        return super(BaseProfile, self).get_pictures(exclude={'id': self.picture.id} if self.picture else {})

    def get_gravatar_url(self, size=r'160x160'):
        """
        Renvoyer l'URL du gravatar pour l'utilisateur

        :param size: chaîne raw indiquant les dimensions du gravatar requis
        """
        gravatar_url = "http://www.gravatar.com/avatar/{}?{}".format(hashlib.md5(self.user.email.lower()).hexdigest(), urllib.urlencode({'s': size}))
        return gravatar_url

    def is_stale(self):
        """ Renvoyer si l'utilisateur est considéré comme abandonné """
        info = check_stale.send(sender=None, profile=self, user=self.user)  # Envoyer le signal de vérification
        return info and False not in [item[1] for item in info]

    def is_unused(self):
        """ Renvoyer si l'utilisateur est totalement inutilisé """
        info = check_unused.send(sender=None, profile=self, user=self.user)  # Envoyer le signal de vérfication
        return info and False not in [item[1] for item in info]

    def get_admin_annotation(self):
        """ Renvoyer la note admin pour ce profil """
        return self.get_data('admin')

    def has_admin_annotation(self):
        """ Renvoyer si le profil a des annotations admin """
        return self.get_admin_annotation() is not None

    # Setter
    def set_picture(self, picture, delete_previous=False):
        """
        Définir l'image principale du profil

        :param picture: instance de content.Picture
        :param delete_previous: supprimer l'ancienne image ?
        """
        previous = self.picture
        if previous is not picture:
            self.picture = picture
            self.save()
            if delete_previous and previous is not None:
                previous.delete()
                return None
            profile_picture_changed.send(sender=self)
            return previous

    def update_gravatar(self, clear=False):
        """ Retélécharger le gravatar du profil """
        gravatar_url = self.get_gravatar_url()
        from scoop.content.models import Picture
        # Supprimer d'abord le gravatar déjà téléchargé
        Picture.objects.by_marker('gravatar', author=self.user).delete(clear=clear)
        return Picture.objects.create_from_uri(gravatar_url, marker='gravatar')

    def ban(self, process=True):
        """ Bannir le profil (si possible) """
        if self.is_bannable() and not self.banned:
            self.banned = True
            self.set_data('baninfo', value={'time': timezone.now()}, save=False)
            self.save(update_fields=['banned', 'updated', 'data'])
            if process:
                profile_banned.send(self, user=self.user)
            return True
        return False

    def toggle_ban(self, process=True):
        """ Basculer l'état de bannissement """
        if self.banned:
            self.banned = False
            self.save(update_fields=['banned', 'updated'])
        else:
            self.ban(process)

    def annotate_admin(self, content):
        """ Définir l'annotation admin pour le profil """
        self.set_data('admin', content)

    def verify(self):
        """ Marquer le profil comme étant vérifié """
        if self.harmful is not False:
            self.harmful = False
            self.save()
            return True
        return False

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode pour l'objet """
        return self.user.__str__()

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(BaseProfile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if kwargs.get('wipe', False):
            super(BaseProfile, self).delete(*args, **kwargs)
        else:
            self.user.deactivate()

    def get_absolute_url(self):
        """ Renvoyer l'URL du profil """
        return self.user.get_absolute_url()

    # Métadonnées
    class Meta:
        abstract = True
