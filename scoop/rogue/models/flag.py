# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from translatable.models import TranslatableModel, get_translation_model

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.util.model.model import SingleDeleteManager, limit_to_model_names
from scoop.core.util.shortcuts import addattr
from scoop.rogue.util.signals import flag_closed, flag_created, flag_resolve


class FlagManager(SingleDeleteManager):
    """ Manager des signalements """

    # Overrides
    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(FlagManager, self).get_queryset()

    # Getter
    def get_flags(self, *args, **kwargs):
        """
        Filtrer les flags dont le type est celui de app.model
        :param days: flags plus récents que <days> jours
        :param model: app_label.model indiquant sur quel type d'objets filtrer
        """
        if 'model' in kwargs:
            app_model = kwargs['model'].split('.')
            content_type = ContentType.objects.get(app_label=app_model[0], model=app_model[1])
            flags = self.filter(type__content_type=content_type).order_by('-id')
        else:
            flags = self.all()
        # Uniquement les flags plus récents qu'une date
        if 'days' in kwargs:
            flags = flags.filter(time__gt=Flag.get_last_days(kwargs['days']))
        return flags

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
    def flag(self, item, *args, **kwargs):
        """ Signaler un objet """
        try:
            from scoop.rogue.models import FlagType
            # Permettre d'utiliser une chaîne pour type en utilisant typename
            if kwargs.get('typename', False):
                kwargs['type'] = FlagType.objects.get_by_name(kwargs.get('typename'))
                kwargs.pop('typename')
            # Les flags auto ont un auteur robot ou admin
            if kwargs.get('automatic', False):
                kwargs['author'] = get_user_model().objects.get_bot_or_admin()
            # Créer le flag
            flag = Flag(**kwargs)
            flag.content_object = item
            flag.save()
            flag_created.send(sender=flag, flag=flag)
        except:
            pass

    def flag_by_lookup(self, model_name, identifier, *args, **kwargs):
        """ Signaler un objet via app_label.model et id """
        try:
            item = ContentType.get_object_for_this_type(model=model_name, pk=identifier)
            Flag.flag(item, **kwargs)
            return True
        except ContentType.DoesNotExist:
            return False


class Flag(DatetimeModel):
    """ Signalement """
    # Constantes
    STATUSES = [[0, _(u"New")], [1, _(u"Being checked")], [2, _(u"Closed")], [3, _(u"Fixed")], [4, _(u"Will not fix")], [5, _(u"Postponed")], [6, _(u"Pending")]]
    NEW, CHECKING, CLOSED, FIXED, WONTFIX, POSTPONED, PENDING = 0, 1, 2, 3, 4, 5, 6
    # Informations du flag
    name = models.CharField(max_length=128, blank=True, editable=False, verbose_name=_(u"Object name"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='flags_made', on_delete=models.SET_NULL, verbose_name=_(u"Author"))
    type = models.ForeignKey('rogue.FlagType', null=False, related_name='flags', verbose_name=_(u"Type"))
    priority = models.SmallIntegerField(default=2, validators=[MaxValueValidator(5), MinValueValidator(0)], verbose_name=_(u"Priority"))
    status = models.SmallIntegerField(choices=STATUSES, default=NEW, null=False, db_index=True, verbose_name=_(u"Status"))
    details = models.CharField(max_length=128, blank=True, verbose_name=_(u"Details"))
    admin = models.CharField(max_length=128, blank=True, verbose_name=_(u"Administration notes"))
    automatic = models.BooleanField(default=False, db_index=True, editable=False, verbose_name=pgettext_lazy('flag', u"Automatic"))
    action_done = models.BooleanField(default=False, db_index=True, verbose_name=_(u"Action done"))
    updated = models.DateTimeField(default=timezone.now, null=True, verbose_name=pgettext_lazy('flag', u"Updated"))
    objects = FlagManager()
    limit = limit_to_model_names('user.user', 'content.content', 'content.picture')  # limite des modèles concernés
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, limit_choices_to=limit, verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True, verbose_name=_(u"Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    url = models.CharField(max_length=128, blank=True, verbose_name=_(u"URL"))
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='moderated_flags', verbose_name=_(u"Moderators"))

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

    def is_moderated_by(self, user):
        """ Renvoyer si un utilisateur est modérateur du signalement """
        moderator = self.moderators.filter(pk=user.pk).exists()
        superuser = user.is_superuser
        return superuser or moderator

    @addattr(short_description=_(u"Author"))
    def get_author_name(self):
        """ Renvoyer le nom de l'auteur du signalement """
        return self.author or self.name

    def needs_details(self):
        """ Renvoyer si le type de signalement nécessite des détails """
        return self.type.needs_details

    def get_typename(self):
        """ Renvoyer le nom de code du type du signalement """
        return self.type.short_name

    @addattr(allow_tags=True, admin_order_field='content_object', short_description=_(u"Content"))
    def get_content_name(self):
        """ Renvoyer le nom """
        return self.name

    @addattr(allow_tags=True, admin_order_field='status', short_description=_(u"Status"))
    def get_status_html(self):
        """ Renvoyer une représentation HTML du statut du signalement """
        types = {0: u'important', 1: u'warning', 2: u'success', 3: u'success', 4: u'success', 5: u'info', 6: u'info'}
        html = u'<span class="modal-action label label-{css}">{status}</span>'.format(status=self.get_status_display(), css=types[self.status])
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

    def update(self, *args, **kwargs):
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
            result = flag_resolve.send(sender=self, iteration=action_count)
            if [True for item in result if item[1] is True]:
                self.action_done = True
            # Fermer les clones
            if propagate:
                for flag in self.get_clones():
                    flag.update(admin=self.admin)
                    flag.close(Flag.FIXED)  # fixed
        self.close(Flag.FIXED)  # fixed

    def set_admin_notes(self, text):
        """ Définir les notes d'administration du signalement """
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
        # Peupler l'attribut nom
        if self.content_object is not None:
            maxlength = Flag._meta.get_field('name').max_length - 4
            self.name = truncatechars(self.content_object.__unicode__(), maxlength)
        super(Flag, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.content_type = None
        self.object_id = None
        super(Flag, self).delete(*args, **kwargs)

    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return u"{item}@{url}".format(url=self.url, item=self.content_object)

    # Métadonnées
    class Meta:
        verbose_name = _(u"flag")
        verbose_name_plural = _(u"flags")
        unique_together = ('author', 'content_type', 'object_id')
        permissions = (("can_flag", u"Can flag"),
                       ("can_moderate_flag", u"Can moderate flags")
                       )
        app_label = 'rogue'


class FlagTypeManager(SingleDeleteManager):
    """ Manager des types de signalement """

    # Getter
    def get_by_name(self, name):
        """ Renvoyer les types de signalement selon leur nom """
        try:
            result = self.get(short_name__iexact=name)
        except:
            result = None
        return result


class FlagType(TranslatableModel, IconModel):
    """ Type de signalement """
    limit = limit_to_model_names('user.user', 'content.content', 'content.picture')
    short_name = models.CharField(max_length=20, verbose_name=_(u"Identifier"))
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, verbose_name=_(u"Content type"), limit_choices_to=limit)
    needs_details = models.BooleanField(default=False, verbose_name=_(u"Needs details"))
    objects = FlagTypeManager()

    # Getter
    @addattr(short_description=_(u"Name"))
    def get_name(self):
        """ Renvoyer le nom du type de signalement """
        try:
            return self.get_translation().name
        except:
            return _(u"(No name)")

    @addattr(short_description=_(u"Description"))
    def get_description(self):
        try:
            return self.get_translation().description
        except:
            return _(u"(No description)")

    # Propriétés
    name = property(get_name)
    description = property(get_description)

    # Overrides
    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if not self.content_set.all().exists():
            super(FlagType, self).delete(*args, **kwargs)

    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        try:
            return self.get_translation().name
        except:
            return _(u"None")

    # Métadonnées
    class Meta:
        verbose_name = _(u"flag type")
        verbose_name_plural = _(u"flag types")
        app_label = 'rogue'


class FlagTypeTranslation(get_translation_model(FlagType, "flagtype"), TranslationModel):
    """ Traduction de type de signalement """
    name = models.CharField(max_length=96, blank=False, verbose_name=_(u"Name"))
    description = models.TextField(blank=True, verbose_name=_(u"Description"))

    # Métadonnées
    class Meta:
        app_label = 'rogue'
