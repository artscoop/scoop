# coding: utf-8
import datetime
import logging
from datetime import timedelta
from os.path import join

from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import ContentType
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from pretty_times import pretty
from scoop.core.util.data.dateutil import datetime_round_hour
from scoop.core.util.data.typeutil import get_color_name, hash_rgb
from scoop.core.util.model.csvexport import csv_dump
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.directory import Paths

logger = logging.getLogger(__name__)


class RecordManager(SingleDeleteManager):
    """ Manager des enregistrements """

    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(RecordManager, self).get_queryset()

    # Actions
    def dump(self, queryset):
        """ Consigner les données dans un fichier CSV """
        if queryset.model == Record:
            fmt = timezone.now().strftime
            filename_info = {'year': fmt("%Y"), 'month': fmt("%m"), 'week': fmt("%W"), 'day': fmt("%d"), 'hour': fmt("%H"), 'minute': fmt("%M"),
                             'second': fmt("%S"), 'rows': queryset.count()}
            path = join(Paths.get_root_dir('isolated', 'var', 'log'), "record-log-{year}-{month}-{day}-{hour}-{minute}-{rows}.csv.gz".format(**filename_info))
            csv_dump(queryset, path, compress=True)

    # Getter
    @staticmethod
    def get_time(value=None):
        """
        Renvoyer une heure, arrondie à zéro minutes

        :returns: ex. 20h19 → 20h00, 20h59 → 20h00
        """
        if value is None:
            value = timezone.now()
        return datetime_round_hour(value)

    def actions_by_user(self, user, codename=None):
        """ Renvoyer toutes les actions d'un utilisateur """
        criteria = {'type__codename': codename} if codename else {}
        return self.filter(user=user, **criteria).order_by('id')

    def by_hour(self, value=None):
        """ Renvoyer toutes les actions d'une certaine heure """
        start = RecordManager.get_time(value)
        end = start + datetime.timedelta(hours=1, microseconds=-1)
        return self.filter(created__range=(start, end))

    # Setter
    def record(self, user, codename, target=None, container=None):
        """
        Enregistrer une nouvelle action

        :param user: instigateur de l'action
        :param codename: nom d'action en 3 parties séparées par des points, du type app.action.model
        :param target: objet concerné par l'action de user
        :type target: models.Model | str | object
        :param container: si target est dans un conteneur, l'ajouter
        """
        try:
            target_object = target if isinstance(target, models.Model) else None
            target_name = str(target) if target is not None else ""
            action_type = RecordType.objects.get(codename=codename)
            entry = Record(user=user, type=action_type, target_object=target_object, target_name=target_name,
                           container_object=container)
            entry.save()
        except RecordType.DoesNotExist:
            logger.warning("The action type {type} must be registered in order to create this record.".format(type=codename))


class RecordTypeManager(SingleDeleteManager):
    """ Manager des types d'actions """

    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(RecordTypeManager, self).get_queryset()

    # Getter
    def get_by_name(self, name):
        """ Renvoyer le type d'action portant un nom de code """
        try:
            return self.get(codename=name)
        except Record.DoesNotExist:
            return None


class Record(models.Model):
    """ Action """

    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='action_records', verbose_name=_("User"))
    name = models.CharField(max_length=32, verbose_name=_("Name"))
    type = models.ForeignKey('core.RecordType', related_name='records', verbose_name=_("Action type"))
    created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=pgettext_lazy('record', "Created"))
    # Cible de l'action
    target_type = models.ForeignKey('contenttypes.ContentType', related_name='target_record', null=True, verbose_name=_("Target type"))
    target_id = models.PositiveIntegerField(null=True, db_index=True, verbose_name=_("Target Id"))
    target_object = fields.GenericForeignKey('target_type', 'target_id')
    target_object.short_description = _("Target")
    target_name = models.CharField(max_length=80, verbose_name=_("Target name"))
    # Conteneur de la cible de l'action
    container_type = models.ForeignKey('contenttypes.ContentType', related_name='container_record', null=True, verbose_name=_("Container type"))
    container_id = models.PositiveIntegerField(null=True, db_index=True, verbose_name=_("Container Id"))
    container_object = fields.GenericForeignKey('container_type', 'container_id')
    container_object.short_description = _("Container")
    container_name = models.CharField(max_length=80, verbose_name=_("Container name"))
    objects = RecordManager()

    # Getter
    @addattr(short_description=_("Description"))
    def get_description(self):
        """ Renvoyer le texte descriptif de l'action """
        output = self.type.sentence % {'actor': self.user, 'target': self.target_object or self.target_name,
                                       'container': self.container_object or self.container_name,
                                       'when': self.get_datetime_ago()}
        return output

    @addattr(admin_order_field='hour', short_description=_("Hour"))
    def get_hour_format(self):
        """ Renvoyer la représentation texte de l'heure de l'action """
        return self.created.strftime("%Y.%m.%d %Hh")

    @addattr(admin_order_field='time', short_description=pgettext_lazy("datetime", "Time"))
    def get_datetime_ago(self):
        """ Renvoyer la date relative de l'action """
        return pretty.date(self.created)

    def get_near(self, delta=1800):
        """ Renvoyer les enregistrements à n secondes près """
        return Record.objects.filter(created__range=(self.created - timedelta(seconds=delta), self.created + timedelta(seconds=delta)))

    def get_type_count(self, delta=1800):
        """ Renvoyer les enregistrements du même type, à n secondes près """
        return self.get_near(delta).filter(type=self.type).exclude(user=self.user).count()

    def get_duplicate_count(self, delta=1800):
        """ Renvoyer le nombre d'enregistrements identiques du même auteur, à n secondes près """
        return self.get_near(delta).filter(type=self.type, user=self.user).count() - 1

    @addattr(allow_tags=True, short_description=_("Color"))
    def get_color_legend(self):
        """ Renvoyer la vignette de légende couleur de l'action """
        return self.type.get_color_legend()

    @addattr(short_description=_("Verbosity"))
    def get_verbosity(self):
        """
        Renvoyer le niveau de verbosité du message

        Renvoie le niveau de verbosité à partir duquel l'enregistrement
        apparaît dans une liste.
        """
        return self.type.verbosity

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.name == '' and self.user is not None:
            self.name = self.user.get_short_name()
        if self.target_name == '' and self.target_object is not None:
            self.target_name = self.target_object.__str__()
        if self.container_name == '' and self.container_object is not None:
            self.container_name = self.container_object.__str__()
        super(Record, self).save(*args, **kwargs)

    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.get_description()

    # Propriétés
    description = property(get_description)

    # Métadonnées
    class Meta:
        verbose_name = _("record")
        verbose_name_plural = _("records")
        app_label = "core"


class RecordType(models.Model):
    """
    Type d'action enregistrable

    :attr codename: nom de code de la forme app.a.b.c.. etc
    :attr sentence: phrase formatable de l'action. Utilise les placeholders {actor}, {target}, {container} et {when}
    """

    # Champs
    codename = models.CharField(max_length=32, verbose_name=_("Code name"))
    sentence = models.CharField(max_length=48, verbose_name=_("Sentence"))  # actor, target, container, when
    verb = models.CharField(max_length=24, verbose_name=_("Verb"))
    verbosity = models.SmallIntegerField(default=0, verbose_name=_("Level of visibility"))
    objects = RecordTypeManager()

    # Getter
    @addattr(allow_tags=True, short_description=_("Color"))
    def get_color_legend(self):
        """ Renvoyer la vignette de code couleur du type d'action """
        rgb = hash_rgb(self.codename)
        colorname = get_color_name(rgb)
        output = """<span class="pill" style="background-color: rgb({r},{g},{b});" title="{name}"></span>"""
        output = output.format(r=rgb[0], g=rgb[1], b=rgb[2], name=colorname)
        return mark_safe(output)

    @addattr(boolean=True, short_description=_("Valid"))
    def is_valid(self):
        """ Renvoyer si le nom de code est correct """
        codeparts = self.codename.split('.')
        length = len(codeparts)
        app_label = codeparts[0]
        return length >= 2 and ContentType.objects.filter(app_label=app_label).exists()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.verb or self.codename

    # Métadonnées
    class Meta:
        verbose_name = _("action type")
        verbose_name_plural = _("action types")
        app_label = "core"
