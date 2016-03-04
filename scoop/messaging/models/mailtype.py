# coding: utf-8
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, TranslatableModelManager, get_translation_model


class MailTypeManager(SingleDeleteManager, TranslatableModelManager):
    """
    Manager des types de courriers électroniques
    """

    # Getter
    def output_types(self):
        """ Renvoie un résumé rapide des types de mail existants """
        output = []
        for item in self.all():
            output.append("{name}\n{description}\n".format(name=item.short_name, description=item.get_description()))
        return "".join(output)

    def get_named(self, name):
        """ Renvoie l'instance MailType possédant un short_name """
        return self.get(short_name__iexact=name)


class MailType(TranslatableModel):
    """
    Type de mail

    Les types de mail possèdent des noms courts du type "app.model.action"
    Exemples courants :
    - messaging.message.new (message)
    - messaging.message.staff (message, staff)
    - user.activation (account, important)
    - content.picture.approved (moderation, staff)
    - etc.
    """

    # Constantes
    CATEGORIES = ['online', 'important']
    INTERVALS = [[0, _("As soon as possible")], [5, _("Every 5 minutes")], [10, _("Every 10 minutes")],
                 [30, _("Every 30 minutes")], [60, _("Every hour")], [720, _("Every 12 hours")],
                 [1440, _("Every day")], [4320, _("Every 3 days")], [10080, _("Every week")], [43200, _("Every 30 days")]]

    # Champs
    short_name = models.CharField(max_length=32, blank=False, unique=True, verbose_name=_("Codename"))
    category = models.CharField(max_length=32, default='', blank=True, help_text=_("Categories, comma separated"), verbose_name=_("Category"))
    template = models.CharField(max_length=32, help_text=_("Template filename without path and extension"), verbose_name=_("Template"))
    interval = models.IntegerField(default=0, choices=INTERVALS, help_text=_("Delay in minutes"), verbose_name=_("Minimum delay"))
    objects = MailTypeManager()

    # Getter
    @addattr(short_description=_("Description"))
    def get_description(self):
        """ Renvoyer la description du type de mail """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _("(No description)")

    @addattr(admin_order_field='interval', short_description=_("Interval"))
    def get_interval(self):
        """ Renvoyer l'intervalle d'envoi pour ce type de mail """
        return datetime.timedelta(minutes=self.interval)

    @addattr(short_description=_("Categories"))
    def get_categories(self):
        """ Renvoyer la liste des catégories liées au type de mail """
        return [name.lower().strip() for name in self.category.split(',') if name]

    def has_category(self, name):
        """ Renvoie si le type de mail est dans une catégorie """
        return name.lower() in self.get_categories()

    # Propriétés
    description = property(get_description)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.short_name

    # Métadonnées
    class Meta:
        verbose_name = _("mail type")
        verbose_name_plural = _("mail types")
        app_label = "messaging"


class MailTypeTranslation(get_translation_model(MailType, "mailtype"), TranslationModel):
    """ Traduction du type de mail """
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(MailTypeTranslation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        app_label = 'messaging'
