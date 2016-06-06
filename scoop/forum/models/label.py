# coding: utf-8
from autoslug.fields import AutoSlugField
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID32Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.model.model import SingleDeleteQuerySet
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model


class LabelManager(SingleDeleteQuerySet):
    """ Manager des étiquettes """

    # Getter
    def visible(self):
        """ Renvoyer les étiquettes publiées """
        return self.filter(visible=True)

    def primary(self):
        """
        Renvoyer les étiquettes principales

        Les étiquettes principales correspondent à des sections de forum
        """
        return self.filter(primary=True)

    def moderated_by(self, user):
        """ Renvoyer les étiquettes modérées par un utilisateur """
        if user.is_superuser:
            return self
        else:
            return self.filter(moderators__pk=user.pk).distinct()

    def get_by_slug(self, slug):
        """ Renvoyer une étiquette selon son slug """
        return self.get(slug=slug)


class Label(TranslatableModel, UUID32Model, WeightedModel):
    """ Étiquette d'une discussion """

    # Champs
    parent = models.ForeignKey('self', null=True, blank=False, limit_choices_to={'primary': True}, related_name='children', verbose_name=_("Parent"))
    short_name = models.CharField(max_length=24, blank=False, unique=True, verbose_name=_("Short name"))
    slug = AutoSlugField(max_length=32, populate_from='short_name', unique=True, blank=True, editable=True, unique_with=('uuid',))
    primary = models.BooleanField(default=True, help_text=_("Can be set at thread creation"), verbose_name=pgettext_lazy('label', "Primary"))
    status = models.BooleanField(default=False, help_text=_("Does the label define the status of the thread"), verbose_name=_("Status"))
    visible = models.BooleanField(default=True, verbose_name=pgettext_lazy('label', "Visible"))
    groups = models.ManyToManyField('auth.Group', blank=True, related_name='forum_labels', verbose_name=_("Groups allowed"))
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='+', limit_choices_to={'is_staff': True},
                                        verbose_name=_("Moderators"))
    objects = LabelManager.as_manager()

    # Getter
    def is_moderator(self, user):
        """
        Renvoyer si un utilisateur est modérateur du label

        :param user: Utilisateur
        """
        return user.is_superuser or self.moderators.filter(pk=user.pk).exists()

    def is_visible(self, user):
        """
        Renvoyer si un utilisateur peut voir l'étiquette et ses contenus

        :param user: utilisateur
        """
        is_admin = user.is_superuser or user.is_staff
        is_in_group = self.groups.filter(pk__in=user.groups.values_list('pk')).exists()
        is_moderator = self.moderators.filter(pk=user.pk).exists()
        return is_admin or is_moderator or (self.visible and is_in_group)

    def get_name(self):
        """ Renvoyer le nom du label """
        try:
            return self.get_translation().name
        except MissingTranslation:
            return _("Unnamed")

    def get_description(self):
        """ Renvoyer la description du label """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _("No description")

    def get_html(self):
        """ Renvoyer la description HTML du label """
        try:
            return self.get_translation().html
        except MissingTranslation:
            return _("No description")

    def get_children(self):
        """ Renvoie les descendants de l'étiquette """
        return self.children.all()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation de l'objet """
        return _("Forum label: [{name}]").format(name=self.name)

    # Propriétés
    name = property(get_name)
    description = property(get_description)
    html = property(get_html)

    # Métadonnées
    class Meta:
        verbose_name = _("Label")
        verbose_name_plural = _("Labels")
        app_label = 'forum'


class LabelTranslation(get_translation_model(Label, "label"), TranslationModel):
    """ Traduction de type de contenu """

    # Champs
    name = models.CharField(max_length=64, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    html = models.TextField(blank=True, verbose_name=_("HTML description"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(LabelTranslation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("translation")
        verbose_name_plural = _("translations")
        app_label = 'forum'


class LabelledModel(models.Model):
    """ Mixin de modèle associé à des étiquettes de forum """

    # Champs
    main_label = models.ForeignKey('forum.Label', null=True, limit_choices_to={'primary': True}, related_name='+', verbose_name=_("Main label"))
    status_label = models.ForeignKey('forum.Label', null=True, limit_choices_to={'status': True}, related_name='+', verbose_name=_("Status label"))
    labels = models.ManyToManyField('forum.Label', blank=True, limit_choices_to={'primary': False, 'status': False}, related_name='+', verbose_name=_("Labels"))

    # Getter
    def get_all_labels(self):
        """ Renvoyer toutes les étiquettes """
        labels = [self.main_label, self.status_label]
        for label in self.labels.all():
            labels.append(label)
        return filter(None, labels)

    def is_global(self):
        """ Renvoyer si l'objet apparaît dans toutes les catégories """
        return self.main_label is None

    def is_label_visible(self, request_or_user):
        """ Renvoyer si l'étiquette principale de l'objet est accessible à l'utilisateur """
        user = getattr(request_or_user, 'user', request_or_user)
        return self.main_label.is_visible(user)

    # Métadonnées
    class Meta:
        abstract = True
