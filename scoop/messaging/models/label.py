# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


class LabelManager(SingleDeleteManager):
    """ Manager des étiquettes """

    # Getter
    def for_user(self, user):
        """ Renvoyer les étiquettes d'un utilisateur """
        return self.filter(user=user)


class Label(DatetimeModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='thread_labels', verbose_name=_("Author"))
    name = models.CharField(blank=False, max_length=40, validators=[RegexValidator(r'^[\d\w][\d\s\w]*$', _("Must contain only letters and digits"))], db_index=True, verbose_name=_("Name"))
    objects = LabelManager()

    # Getter
    def get_item_count(self, model_list, per_class=False):
        """ Renvoyer le nombre d'instances d'un ou plusieurs modèles avec cette étiquette """
        count = {} if per_class else 0
        if not isinstance(model_list, list):
            model_list = [model_list]
        for model in model_list:
            if issubclass(model, LabelableModel):
                total = model.objects.filter(labels=self).count()
                if per_class is True:
                    count[model] = total
                else:
                    count = count + total
        return count

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.name = self.name.lower().strip()
        super(Label, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("label")
        verbose_name_plural = _("labels")
        unique_together = (('user', 'name'),)
        app_label = 'messaging'


class LabelableModel(models.Model):
    """ Mixin de modèle pouvant avoir des étiquettes """
    labels = models.ManyToManyField('messaging.label', blank=True, verbose_name=_("Labels"))

    # Getter
    def get_labels(self):
        """ Renvoyer les étiquettes de l'élément """
        return self.labels.all()

    def get_labels_for(self, user):
        """ Renvoyer les étiquettes sur l'élément créées par un utilisateur """
        return self.labels.filter(user=user)

    @addattr(short_description=_("Labels"))
    def get_label_count(self):
        """ Renvoyer le nombre d'étiquettes """
        return self.labels.all().count()

    # Setter
    def add_label(self, author, name):
        """ Ajouter une étiquette à l'objet """
        label, _ = Label.objects.get_or_create(user=author, name=name.strip().lower())
        self.labels.add(label)

    def remove_label(self, author, name):
        """ Retirer une étiquette à l'objet """
        labels = Label.objects.filter(user=author, name=name.strip().lower())
        for label in labels:
            self.labels.remove(label)

    # Métadonnées
    class Meta:
        abstract = True
