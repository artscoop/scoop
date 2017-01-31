# coding: utf-8
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.transaction import TransactionManagementError
from django.db.utils import OperationalError
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.model.model import SingleDeleteManager, limit_to_model_names
from scoop.core.util.shortcuts import addattr
from scoop.rogue.util.signals import flag_closed, flag_created, flag_resolve
from translatable.models import TranslatableModel, get_translation_model


class FlagManager(SingleDeleteManager):
    """ Manager des signalements """

    # Overrides
    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(FlagManager, self).get_queryset()

    # Getter
    def filter(self, **kwargs):
        """
        Filtrer les flags dont le type est celui de app.model

        :param days: flags plus récents que <days> jours
        :param model: app_label.model indiquant sur quel type d'objets filtrer
        :type model: str
        :type days: int
        """
        app_model = [part for part in kwargs.pop('model', '').split('.', 1) if part]
        days = kwargs.pop('days', None)

        if app_model:
            content_type = ContentType.objects.get(app_label=app_model[0], model=app_model[1])
            kwargs['type__content_type'] = content_type

        if days is not None:
            kwargs['time__gt'] = Flag.get_last_days(days)
        return super(FlagManager, self).filter(**kwargs)

    def get_user_flag_count(self, user):
        """ Renvoyer le nombre de signalements envoyés par un utilisateur """
        count = self.filter(author=user).count()
        return count

    def by_typename(self, name):
        """ Renvoyer les signalements d'un certain nom de type """
        return self.filter(type__short_name__iexact=name)

    def for_target(self, target):
        """ Renvoyer tous les signalements sur un objet """
        content_type = ContentType.objects.get_for_model(target)
        return Flag.objects.filter(content_type=content_type, object_id=target.pk).order_by('-id')

    def get_for_target_count(self, target):
        """ Renvoyer le nombre de signalements sur un objet """
        return self.for_target(target).count()

    # Setter
    def flag(self, item, **kwargs):
        """
        Signaler un objet

        :param item: Cible du signalement
        :param kwargs:
            type_name (obligatoire) : nom de code du type de signalement
        """
        if 'author' not in kwargs or kwargs['author'].has_perm('rogue.can_flag'):
            try:
                from scoop.rogue.models import FlagType
                # Permettre d'utiliser une chaîne pour type en utilisant typename
                if kwargs.get('type_name', False):
                    kwargs['type'] = FlagType.objects.get_by_name(kwargs.pop('type_name'))
                # Les flags auto ont un auteur robot ou admin
                if kwargs.get('automatic', False):
                    kwargs['author'] = get_user_model().objects.get_bot_or_admin()
                # Créer le flag
                flag = Flag(**kwargs)
                flag.update(content_object=item, save=True)
                flag_created.send(sender=flag.content_type, flag=flag)
                return True
            except (TransactionManagementError, OperationalError):
                pass
        return False

    def flag_by_lookup(self, model_name, identifier, *args, **kwargs):
        """
        Signaler un objet via app_label.model et id

        :param model_name: nom de modèle Django
        :param identifier: identifiant de l'objet, ou identifiants
        :type identifier: int | list
        """
        identifiers = make_iterable(identifier)
        for identifier in identifiers:
            try:
                item = ContentType.get_object_for_this_type(model=model_name, pk=identifier)
                self.flag(item, **kwargs)
                return True
            except ContentType.DoesNotExist:
                return False


class Flag(DatetimeModel):
    """ Signalement """

    # Constantes
    STATUSES = [[0, _("New")], [1, _("Being checked")], [2, _("Closed")], [3, _("Fixed")], [4, _("Will not fix")], [5, _("Postponed")], [6, _("Pending")]]
    PRIORITIES = [[0, _("Lowest")], [1, _("Low")], [2, _("Medium")], [3, _("High")], [4, _("Critical")]]
    NEW, CHECKING, CLOSED, FIXED, WONTFIX, POSTPONED, PENDING = 0, 1, 2, 3, 4, 5, 6
    LOWEST, LOW, MEDIUM, HIGH, CRITICAL = 0, 1, 2, 3, 4

    # Champs
    name = models.CharField(max_length=128, blank=True, editable=False, verbose_name=_("Object name"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='flags_made', on_delete=models.SET_NULL, verbose_name=_("Author"))
    type = models.ForeignKey('rogue.FlagType', null=False, related_name='flags', verbose_name=_("Type"))
    priority = models.SmallIntegerField(default=MEDIUM, choices=PRIORITIES, validators=[MaxValueValidator(4), MinValueValidator(0)], verbose_name=_("Priority"))
    status = models.SmallIntegerField(choices=STATUSES, default=NEW, null=False, db_index=True, verbose_name=_("Status"))
    details = models.CharField(max_length=128, blank=True, verbose_name=_("Details"))
    admin = models.CharField(max_length=128, blank=True, verbose_name=_("Administration notes"))
    automatic = models.BooleanField(default=False, db_index=True, editable=False, verbose_name=pgettext_lazy('flag', "Automatic"))
    action_done = models.BooleanField(default=False, db_index=True, verbose_name=_("Action done"))
    updated = models.DateTimeField(default=timezone.now, null=True, verbose_name=pgettext_lazy('flag', "Updated"))
    limit = limit_to_model_names('user.user', 'content.content', 'content.picture')  # limite des modèles concernés
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, limit_choices_to=limit, verbose_name=_("Content type"))
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True, verbose_name=_("Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    object_owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("Owner"))
    url = models.CharField(max_length=192, blank=True, verbose_name=_("URL"))
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='moderated_flags', verbose_name=_("Moderators"))
    objects = FlagManager()

    # Getter
    def get_siblings(self):
        """ Renvoyer les signalements avec la même cible """
        return Flag.objects.filter(content_type=self.content_type, object_id=self.object_id).order_by('-id')

    def get_sibling_count(self):
        """ Renvoyer le nombre de signalements avec la même cible """
        return self.get_siblings().count()

    def get_clones(self):
        """ Renvoyer les signalements avec la même cible, et du même type """
        return self.get_siblings().filter(type=self.type)

    def get_clone_count(self, exclude=False):
        """ Renvoyer le nombre de signalements avec la même cible, et du même type """
        return self.get_clones().count() - (1 if exclude else 0)

    def get_moderators(self):
        """ Renvoyer les modérateurs du signalement """
        return self.moderators.all()

    def is_moderated_by(self, user):
        """ Renvoyer si un utilisateur est modérateur du signalement """
        moderator = self.moderators.filter(pk=user.pk)
        superuser = user.is_superuser
        return superuser or moderator.exists()

    @addattr(short_description=_("Author"))
    def get_author_name(self):
        """ Renvoyer le nom de l'auteur du signalement """
        return self.author or self.name

    def needs_details(self):
        """ Renvoyer si le type de signalement nécessite des détails """
        return self.type.needs_details

    def get_typename(self):
        """ Renvoyer le nom de code du type du signalement """
        return self.type.short_name

    @addattr(allow_tags=True, admin_order_field='content_object', short_description=_("Content"))
    def get_content_name(self):
        """ Renvoyer le nom """
        return self.name

    @addattr(allow_tags=True, admin_order_field='status', short_description=_("Status"))
    def get_status_html(self):
        """ Renvoyer une représentation HTML du statut du signalement """
        types = {0: 'important', 1: 'warning', 2: 'success', 3: 'success', 4: 'success', 5: 'info', 6: 'info'}
        html = '<span class="modal-action label label-{css}">{status}</span>'.format(status=self.get_status_display(), css=types[self.status])
        return mark_safe(html.encode('utf-8'))

    def get_priority_class(self):
        """ Renvoyer une classe CSS selon la priorité du signalement """
        levels = {'info': (0, 1), 'warning': (2, 3), 'error': (4, 100)}
        for level in levels:
            if levels[level][0] <= self.priority <= levels[level][1]:
                return level

    # Setter
    def close(self, status=CLOSED):
        """ Fermer le signalement """
        if status in {Flag.CLOSED, Flag.FIXED, Flag.WONTFIX}:
            self.status = status
            self.save(update_fields=['status'])
            flag_closed.send(sender=self)

    def update_status(self, *args, **kwargs):
        """ Mettre à jour le statut du signalement """
        self.status = kwargs.get('status', self.status)
        self.details = kwargs.get('details', self.details)
        self.admin = kwargs.get('admin', self.admin)
        self.save()

    def resolve(self, propagate=True):
        """
        Résoudre automatiquement un signalement via listeners

        :param propagate: attribuer la résolution aux flags identiques
        """
        if not self.action_done:
            action_count = self.get_siblings().filter(action_done=True).count()
            # Envoyer un signal. Les gestionnaires liés renvoient True ou False
            # Si l'un des gestionnaires renvoie True, une mesure a été prise.
            result = flag_resolve.send(sender=self.content_type.model_class(), flag=self, iteration=action_count)
            if any([item[1] is True for item in result]):
                self.action_done = True
            # Fermer les clones
            if propagate:
                for flag in self.get_clones():
                    flag.update(admin=self.admin)
                    flag.close(Flag.FIXED)
        self.close(Flag.FIXED)

    def set_admin_notes(self, text):
        """
        Définir les notes d'administration du signalement

        :type text: str
        """
        self.admin = text
        self.save(update_fields=['admin'])

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        # Réparer le signalement s'il ne correspond pas à son type
        if self.content_type != self.type.content_type:
            self.content_object = None
        # Au minimum, l'URL doit contenir un slash
        self.url = '/' if not self.url else self.url
        # Peupler l'attribut nom et object_owner
        if self.content_object is not None:
            maxlength = Flag._meta.get_field('name').max_length - 4
            self.name = truncatechars(str(self.content_object), maxlength)
            author = getattr(self.content_object, 'author', None)
            self.object_owner = author
        super(Flag, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.content_type = None
        self.object_id = None
        super(Flag, self).delete(*args, **kwargs)

    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "\u26a0{item}@{url}".format(url=self.url, item=self.content_object)

    # Métadonnées
    class Meta:
        verbose_name = _("flag")
        verbose_name_plural = _("flags")
        unique_together = ('author', 'content_type', 'object_id')
        permissions = (("flag_content", "Can flag"),
                       ("moderate_flag", "Can moderate flags"))
        app_label = 'rogue'


class FlagTypeManager(SingleDeleteManager):
    """ Manager des types de signalement """

    # Getter
    def get_by_name(self, name):
        """ Renvoyer les types de signalement selon leur nom """
        try:
            result = self.get(short_name__iexact=name)
        except FlagType.DoesNotExist:
            result = None
        return result


class FlagType(TranslatableModel, IconModel):
    """ Type de signalement """

    # Champs
    limit = limit_to_model_names('user.user', 'content.content', 'content.picture')
    short_name = models.CharField(max_length=20, verbose_name=_("Identifier"))
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, verbose_name=_("Content type"), limit_choices_to=limit)
    needs_details = models.BooleanField(default=False, verbose_name=_("Needs details"))
    objects = FlagTypeManager()

    # Getter
    @addattr(short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom du type de signalement """
        try:
            return self.get_translation().name
        except FlagTypeTranslation.DoesNotExist:
            return _("(No name)")

    @addattr(short_description=_("Description"))
    def get_description(self):
        try:
            return self.get_translation().description
        except FlagTypeTranslation.DoesNotExist:
            return _("(No description)")

    # Propriétés
    name = property(get_name)
    description = property(get_description)

    # Overrides
    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if not self.content_set.all().exists():
            super(FlagType, self).delete(*args, **kwargs)

    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.get_name()

    # Métadonnées
    class Meta:
        verbose_name = _("flag type")
        verbose_name_plural = _("flag types")
        app_label = 'rogue'


class FlagTypeTranslation(get_translation_model(FlagType, "flagtype"), TranslationModel):
    """ Traduction de type de signalement """

    # Champs
    name = models.CharField(max_length=96, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Métadonnées
    class Meta:
        app_label = 'rogue'
