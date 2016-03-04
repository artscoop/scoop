# coding: utf-8
import datetime
import time
from datetime import timedelta

import qsstats
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import UserManager as DefaultManager
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser, PermissionsMixin
from django.contrib.contenttypes.fields import ContentType
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import permalink
from django.http import Http404
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.util.django.apps import is_installed
from scoop.core.util.model.model import SingleDeleteQuerySetMixin
from scoop.core.util.shortcuts import addattr
from scoop.user.util.signals import check_stale, online_status_updated, user_activated, user_deactivated


class UserQuerySetMixin(object):
    """ Mixin du QuerySet et du Manager des utilisateurs """

    # Getter
    def by_request(self, request):
        """ Renvoyer les utilisateurs accessibles depuis la requête """
        return self.filter(is_active=True, deleted=False, bot=False).exclude(pk=0) if (request and not request.user.is_staff) else self

    def active(self):
        """ Renvoyer les utilisateurs normaux actifs """
        return self.filter(is_active=True, deleted=False, bot=False)

    def deleted(self):
        """ Renvoyer les utilisateurs supprimés """
        return self.filter(deleted=True)

    def get_by_natural_key(self, username):
        """ Renvoyer un utilisateur par sa clé naturelle """
        return self.get(username=username)

    def get_or_none(self, **kwargs):
        """ Renvoyer un utilisateur selon des paramètres de filtre, ou None """
        user = self.filter(**kwargs)[:1]
        return user.get() if user.exists() else None

    def get_or_raise(self, **kwargs):
        """
        Renvoyer un utilisateur selon des paramètres de filtre, sinon lever une exception
        :param exception: classe de l'exception à lever en cas d'absence de l'utilisateur
        """
        exception = kwargs.pop('exception', Http404)
        user = self.filter(**kwargs)
        if not user.exists():
            raise exception()
        return user[0]

    def get_or_404(self, **kwargs):
        """ Renvoyer un utilisateur selon des paramètres de filtre, sinon lever un 404 """
        return self.get_or_raise(exception=Http404, **kwargs)

    def get_by_id(self, identifier, user=AnonymousUser(), exception=Http404, **kwargs):
        """ Renvoyer un utilisateur selon son id, sinon un utilisateur par défaut ou une exception """
        [kwargs.pop(key, None) for key in {'pk', 'id'}]
        value = self.get_or_raise(pk=int(identifier), exception=exception, **kwargs) if identifier else user
        if value == AnonymousUser() and exception:
            raise exception()
        return value

    def get_by_name(self, name):
        """ Renvoyer un utilisateur par son nom d'utilisateur """
        return self.get_or_none(username=name)

    def get_by_email(self, email):
        """ Renvoyer un utilisateur avec une adresse email """
        try:
            return self.get(email__iexact=email)
        except User.DoesNotExist:
            return False

    def get_by_uuid(self, uuid, user=None, **kwargs):
        """ Renvoyer un utilisateur selon son uuid, sinon un utilisateur par défaut """
        value = self.get_or_404(uuid=uuid, **kwargs) if uuid else (user or AnonymousUser())
        return value

    def by_online_range(self, start, duration):
        """
        Renvoyer des utilisateurs selon la période pendant laquelle ils ont été en ligne
        :param start: datetime de départ
        :param duration: timedelta positif ou négatif d'offset de fin
        """
        online_range = [start, start + duration] if duration > datetime.timedelta() else [start - duration, start]
        return self.filter(last_online__range=online_range)

    def get_bot(self, name=None):
        """ Renvoyer un robot, sinon un superutilisateur, sinon un nouveau robot """
        criteria = {'username': name} if name else {}
        bots = self.filter(bot=True, **criteria)
        if bots.exists():
            return bots.first()
        bots = self.filter(is_superuser=True)
        if bots.exists():
            return bots.first()
        new_bot = self.create(username='bot-{}'.format(slugify(name or "default")), name=name or "Bot", email='rescuebot@localhost.com', bot=True)
        return new_bot

    def get_anonymous(self):
        """ Renvoyer l'utilisateur anonyme """
        user = AnonymousUser()
        user.username = settings.ANONYMOUS_USER_NAME
        return user

    def get_superuser(self, name=None):
        """ Renvoyer le superutilisateur principal """
        criteria = {} if name is None else {'username__iexact': name}
        return self.filter(is_superuser=True, **criteria).order_by('id')[0]

    @is_installed(['rogue', 'access'], None)
    def similar_to(self, user, since=30):
        """ Renvoyer les utilisateurs ayant navigué avec les mêmes adresses IP """
        from scoop.user.access.models import UserIP
        # Définir la date minimum
        last_login_limit = timezone.now() - datetime.timedelta(days=since)
        return UserIP.objects.related_users(user, exclude_self=True).filter(last_login__gte=last_login_limit)

    def get_registration_count(self, hours=720, active=True):
        """ Renvoyer le nombre de nouveaux utilisateurs actifs ou non depuis n heures """
        threshold = timezone.now() - datetime.timedelta(hours=hours)
        return self.filter(date_joined__gte=threshold).count()

    def get_unregistration_count(self, hours=720, active=True):
        """ Renvoyer le nombre d'utilisateurs qui ont été supprimés ces n dernières heures """
        threshold = timezone.now() - datetime.timedelta(hours=hours)
        return self.deleted().filter(last_online__gte=threshold).count()

    def get_date_stats(self, column='date_joined'):
        """ Renvoyer des statistiques de créations de profils """
        qs = qsstats.QuerySetStats(self, column)
        return {'minute': qs.this_minute(), 'hour': qs.this_hour(), 'day': qs.this_day(), 'month': qs.this_month(), 'year': qs.this_year()}

    def get_active_count(self):
        """ Renvoyer le nombre d'utilisateurs actifs """
        return self.active().count()

    # Setter
    def force_logout_all(self):
        """ Demander la déconnexion forcée de tous les utilisateurs en ligne """
        users = User.get_online_users()
        for user in users:
            user.force_logout()


class UserQuerySet(models.QuerySet, UserQuerySetMixin, SingleDeleteQuerySetMixin):
    """ Queryset des utilisateurs """
    pass


class UserManager(DefaultManager.from_queryset(UserQuerySet), BaseUserManager, UserQuerySetMixin):
    """ Manager des utilisateurs """

    def get_queryset(self):
        """ Renvoyer le queryset par défaut des utilisateurs """
        return super(UserManager, self).get_queryset().select_related('profile').exclude(id=0)


class User(AbstractBaseUser, PermissionsMixin, UUID64Model):
    """ Utilisateur """

    # Constantes
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']
    CACHE_KEY = {'online': 'user.profile.online.{}', 'online.set': 'user.profile.online.set', 'online.count': 'user.profile.online.count', 'logout.force': 'user.profile.logout.{}'}
    USERNAME_REGEX = r'^[A-Za-z0-9][A-Za-z0-9_]+$'  # Contient lettres, chiffres et underscores
    USERNAME_REGEX_MESSAGE = _("Your name must start with a letter and can only contain letters, digits and underscores")
    NAME_REGEX = r'^[A-Za-z][A-Za-z0-9_\-]+$'  # Commence par une lettre, suivie de lettres, chiffres, underscore et tirets
    NAME_REGEX_MESSAGE = _("Your name can only contain letters")
    ONLINE_DURATION, AWAY_DURATION = 900, 300

    # Champs
    username = models.CharField(max_length=32, unique=True,
                                validators=[RegexValidator(regex=USERNAME_REGEX, message=USERNAME_REGEX_MESSAGE), MinLengthValidator(4)],
                                verbose_name=_("Username"))
    name = models.CharField(max_length=24, blank=True, validators=[RegexValidator(regex=NAME_REGEX, message=NAME_REGEX_MESSAGE)], verbose_name=_("Name"))
    bot = models.BooleanField(default=False, db_index=False, verbose_name=pgettext_lazy('user', "Bot"))
    email = models.EmailField(max_length=96, unique=True, blank=True, verbose_name=_("Email"))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('user', "Active"))
    deleted = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('user', "Deleted"))
    is_staff = models.BooleanField(default=False, help_text=_("Designates whether the user can log into this admin site."),
                                   verbose_name=pgettext_lazy('user', "Staff"))
    date_joined = models.DateTimeField(default=timezone.now, db_index=False, verbose_name=_("Date joined"))
    last_online = models.DateTimeField(default=None, blank=True, null=True, db_index=True, verbose_name=pgettext_lazy('user', "Last online"))
    next_mail = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Next possible mail for user"))
    objects = UserManager()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        if not self.bot and self.name:
            return "{name}".format(name=self.name or self.username)
        elif self.bot:
            return _("Robot")
        return "{nickname}".format(nickname=self.username)

    def __html__(self):
        """ Renvoyer la représentation HTML de l'objet """
        return """<a href="{url}">{name}</a>""".format(url=self.get_absolute_url(), name=self.username)

    # Actions
    @staticmethod
    def sign(request, data, logout=False, fake=False, direct_user=None):
        """
        Connecter ou déconnecter un utilisateur

        :param request: Une connexion nécessite une requête
        :param data: Dictionnaire de connexion, login et password
        :param logout: Demander une déconnexion
        :param fake: Effectuer une simulation de la connexion uniquement
        :param direct_user: Connecter directement un utilisateur sans identifiants
        """
        if logout is False:
            username, password = data.get('username', None), data.get('password', None)
            if direct_user is not None and not fake:
                auth.login(request, direct_user)
                direct_user.update_online(online=True)
                return direct_user
            if not username or not password:
                raise ValidationError(_("The value passed has no login value"))
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.can_login():
                if fake is False:
                    auth.login(request, user)
                    user.update_online(online=True)
                    return user
            elif user is None:
                raise ValidationError(_("Bad username and/or password."), code=0)
            elif not user.is_active:
                raise ValidationError(_("This account is currently not active."), code=1)
            else:
                raise ValidationError(_("This user cannot log in."), code=2)
        else:
            if fake is False:
                request.user.update_online(online=False)
                auth.logout(request)

    # Online / Offline
    @addattr(boolean=True, admin_order_field='last_login', short_description=_("Online"))
    def is_online(self, seconds=ONLINE_DURATION):
        """ Renvoyer si cet utilisateur est considéré en ligne """
        return User.is_user_online(self.id, seconds)

    def was_online_recently(self, days=3):
        """ Renvoyer si cet utilisateur a été en ligne ces n derniers jours """
        return self.last_online >= timezone.now() - datetime.timedelta(days=days)

    @addattr(boolean=True, admin_order_field='last_login', short_description=_("Away"))
    def is_away(self, seconds=AWAY_DURATION):
        """ Renvoyer si cet utilisateur est en ligne, mais absent """
        return User.is_user_away(self.id, seconds)

    @addattr(short_description=_("Online time"))
    def get_online_time(self):
        """ Renvoyer l'heure du dernier accès à une page """
        value = cache.get(self.CACHE_KEY['online'].format(self.id), 0)
        return datetime.datetime.fromtimestamp(value)

    @addattr(short_description=_("Time online"))
    def get_time_online(self):
        """ Renvoyer le temps écoulé depuis le dernier accès à une page """
        return User.get_user_time_online(self.id)

    # Statique
    @staticmethod
    def get_online_set():
        """ Renvoyer un set d'ID de membres en ligne """
        return cache.get(User.CACHE_KEY['online.set'], set())

    @staticmethod
    def get_online_count(compute=False):
        """ Renvoyer le nombre d'utilisateurs en ligne """
        count = cache.get(User.CACHE_KEY['online.count'], None if compute else 0)
        if count is None:  # aucun résultat et compute est True, recalculer
            online_limit = timezone.now() - timedelta(seconds=User.ONLINE_DURATION)
            count = User.objects.filter(last_online__gt=online_limit).count()
            cache.set(User.CACHE_KEY['online.count'], count, 2592000)
        return count

    @staticmethod
    def get_online_users(**kwargs):
        """ Renvoyer les utilisateurs en ligne """
        user_ids = User.get_online_set()
        kwargs['id__in'] = user_ids
        user_list = User.objects.filter(**kwargs)
        return user_list

    @staticmethod
    def is_user_online(user_id, seconds=ONLINE_DURATION):
        """ Renvoyer si l'utilisateur portant un ID est en ligne """
        value = cache.get(User.CACHE_KEY['online'].format(user_id), None)
        return value is not None and (value + seconds >= time.time())

    @staticmethod
    def is_user_away(user_id, seconds=AWAY_DURATION):
        """ Renvoyer si l'utilisateur portant un ID est en ligne, mais absent """
        return (User.get_user_time_online(user_id) or datetime.timedelta(seconds=0)) >= datetime.timedelta(seconds=seconds)

    @staticmethod
    def get_user_time_online(user_id):
        """ Renvoyer le temps écoulé depuis que l'utilisateur avec un ID a accédé à une page """
        timestamp = int(time.time()) + 1
        value = cache.get(User.CACHE_KEY['online'].format(user_id), 0)
        return datetime.timedelta(seconds=timestamp - value) if value else None

    def update_online(self, online=True):
        """ Mettre à jour l'état en ligne/hors ligne de l'utilisateur """
        is_online = self.is_online()
        key = User.CACHE_KEY['online'].format(self.pk)
        if is_online != online:
            online_status_updated.send(self, online=online)
            if not is_online:
                User._add_to_online_list(self.id)
        cache.set(key, round(time.time()) if online else 0)

    @staticmethod
    def _add_to_online_list(user_id):
        """ Ajouter l'ID d'un utilisateur à la liste des ID de membres en ligne """
        user_ids = cache.get(User.CACHE_KEY['online.set'], set())
        if user_id not in user_ids:
            count = User.get_online_count(compute=False)
            user_ids.add(user_id)
            cache.set(User.CACHE_KEY['online.set'], user_ids, 2592000)
            cache.set(User.CACHE_KEY['online.count'], count + 1, 2592000)

    @staticmethod
    def _clean_online_list():
        """ Nettoyer la liste des utilisateurs connectés """
        now = time.time()
        user_ids = User.get_online_set()
        user_keys = [User.CACHE_KEY['online'].format(user_id) for user_id in user_ids]
        values = cache.get_many(user_keys)
        online = {key: (value is not None and value + User.ONLINE_DURATION >= now) for key, value in values.items()}
        start = count = User.get_online_count()
        for user_id in user_ids:
            user_key = User.CACHE_KEY['online'].format(user_id)
            if not online[user_key]:
                user_ids.discard(user_id)
                count -= 1
        if start > count:
            cache.set(User.CACHE_KEY['online.set'], user_ids, 2592000)
            cache.set(User.CACHE_KEY['online.count'], len(user_ids), 2592000)
        return len(user_ids)

    # Getter
    @staticmethod
    def by_request(request):
        """ Renvoyer les utilisateurs accessibles à l'utilisateur de request """
        return User.objects.by_request(request)

    @staticmethod
    def named(name):
        """ Renvoyer l'utilisateur portant un nom d'utilisateur """
        return User.objects.get_by_name(name)

    @classmethod
    def get_type(cls):
        """ Renvoyer l'objet ContentType pour ce modèle """
        return ContentType.objects.get_for_model(cls)

    def natural_key(self):
        """ Renvoyer un utilisateur par sa clé naturelle """
        return self.username,

    def get_full_name(self):
        """ Renvoyer le nom affiché de l'utilisateur, son nom sinon son login  """
        return self.name or self.username

    def get_short_name(self):
        """ Renvoyer le nom d'utilisateur """
        return self.username

    def get_uuid(self):
        """ Renvoyer l'UUID du profil de l'utilisateur """
        return self.profile.uuid

    def is_bot(self):
        """ Renvoyer si l'utilsateur est un robot """
        return self.bot

    def can_login(self):
        """ Renvoyer si l'utilisateur est autorisé à se connecter """
        if hasattr(self, 'profile'):
            if self.profile.is_banned():
                return False
        return self.is_active

    def is_dummy(self):
        """ Renvoyer si l'utilisateur est un anonyme """
        return self.username == settings.ANONYMOUS_USER_NAME

    def is_stale(self):
        """ Renvoyer si l'utilisateur est laissé à l'abandon """
        results = check_stale.send(User, user=self, profile=self.profile)
        return any([result[1] for result in results])

    def get_picture(self):
        """ Renvoyer l'image principale du profil de l'utilisateur """
        return self.profile.picture

    def is_logout_forced(self):
        """ Renvoyer si une demande de déconnexion est en attente """
        return cache.get(User.CACHE_KEY['logout.force'].format(self.pk), 0) == 1

    def can_send_mail(self):
        """ Renvoyer si un nouveau mail normal peut être envoyé à l'utilisateur """
        return self.next_mail is None or self.next_mail <= timezone.now()

    # Setter
    def force_logout(self, timeout=10800):
        """
        Demander une déconnexion de cet utilisateur

        Nécessite user.middleware.auth.AutoLogoutMiddleware
        """
        cache.set(User.CACHE_KEY['logout.force'].format(self.id), 1, timeout)

    def demote(self):
        """ Retirer les attributs équipe et superutilisateur """
        if self.id != 1 and self.is_superuser or self.is_staff:
            self.is_superuser = False
            self.is_staff = False
            self.save(update_fields=['is_superuser', 'is_staff'])
            return True
        return False

    def encrypt_password(self):
        """ Crypter le mot de passe stocké en clair """
        self.set_password(self.password)
        self.save()

    def reset_next_mail(self):
        """ Avancer l'heure minimum du prochain mail recevable """
        from scoop.user.forms.configuration import ConfigurationForm
        # Calculer la date par rapport à la date actuelle
        self.next_mail = timezone.now() + datetime.timedelta(seconds=ConfigurationForm.get_option_for(self, 'receive_interval'))
        self.save(update_fields=['next_mail'])

    def set_inactive(self):
        """ Désactiver l'utilisateur """
        if self.is_active is True:
            self.is_active = False
            self.save()
            user_deactivated.send(sender=self, user=self, request=None)
            return True
        return False

    def set_active(self):
        """ Activer l'utilisateur """
        if self.is_active is False:
            self.is_active = True
            self.save()
            user_activated.send(sender=self, user=self, request=None, failed=False)
            return True
        return False

    # Permissions
    def can_see(self, user):
        """ Renvoyer si l'utilisateur peut en voir un autre """
        return user is not None and (self.is_staff or self.is_superuser or user.is_active)

    def can_edit(self, user):
        """ Renvoyer si l'utilisateur a des droits de modifications sur un autre """
        return user is not None and self.is_active and (self.pk == user.pk or self.is_superuser or (self.is_staff and self.has_perm('auth.edit_user')))

    def can_delete(self, user):
        """ Renvoyer si l'utilisateur a le droit de supprimer un autre """
        return user is not None and not user.is_superuser and (self.pk == user.pk or self.is_superuser or (self.is_staff and self.has_perm('auth.edit_user')))

    def get_rights_on(self, user):
        """ Renvoyer les droits que l'utilisateur possède sur un autre """
        return {'change': self.can_edit(user), 'delete': self.can_delete(user)}

    # Overrides
    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if self.deleted is False and not self.is_superuser:
            self.deleted = True
            self.name = self.username
            self.username = self.id
            self.email = "user-{name}-{id}@removed.del".format(name=self.name, id=self.id)
            self.save()  # En réalité, on ne supprime jamais un utilisateur

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        fixed_username = self._get_fixed_username()
        if self.username != fixed_username:
            self.username = fixed_username
        super(User, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        """ Renvoyer l'URL de l'utilisateur """
        return 'user:profile-view', [], {'uid': str(self.id), 'name': self.username}

    # Privé
    def _get_fixed_username(self):
        """ Renvoyer le nom d'utilisateur final """
        return slugify(str(self.username))

    # Métadonnées
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        app_label = 'user'
