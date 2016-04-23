# coding: utf-8
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


class LabelManager(SingleDeleteManager):
    """ Manager des étiquettes """

    # Getter
    def by_user(self, user):
        """ Renvoyer les étiquettes d'un utilisateur """
        return self.filter(author=user)


class Label(DatetimeModel):
    """ Étiquette utilisateur """

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name='thread_labels', verbose_name=_("Author"))
    name = models.CharField(max_length=40, validators=[RegexValidator(r'^[\d\w][\d\s\w]*$', _("Must contain only letters and digits"))],
                            blank=False, db_index=True, verbose_name=_("Name"))
    objects = LabelManager()

    # Getter
    def get_item_count(self, model_list, per_class=False):
        """
        Renvoyer le nombre d'instances d'un ou plusieurs modèles avec cette étiquette

        :param per_class: renvoyer un dictionnaire avec le nombre d'instances par classe
        :type per_class: bool
        :param model_list: classe(s) de modèles avec étiquette à recenser
        :type model_list: list | models.Model
        :returns: un dictionnaire {Model:int} ou int
        """
        count = {} if per_class else 0
        model_list = make_iterable(model_list)
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
        unique_together = (('author', 'name'),)
        app_label = 'messaging'


class LabelableModel(models.Model):
    """ Mixin de modèle pouvant avoir des étiquettes """

    # Champs
    labels = models.ManyToManyField('messaging.label', blank=True, verbose_name=_("Labels"))

    # Getter
    @addattr(short_description=_("Labels"))
    def get_labels(self):
        """ Renvoyer les étiquettes de l'élément """
        return self.labels.all()

    def get_labels_for(self, user):
        """ Renvoyer les étiquettes sur l'élément créées par un utilisateur """
        return self.labels.filter(author=user)

    @addattr(short_description=_("Labels"))
    def get_label_count(self):
        """ Renvoyer le nombre d'étiquettes """
        return self.labels.all().count()

    # Setter
    def add_label(self, author, name):
        """ Ajouter une étiquette à l'objet """
        label, created = Label.objects.get_or_create(author=author, name=name.strip().lower())
        self.labels.add(label)
        return created

    def remove_label(self, author, name):
        """ Retirer une étiquette à l'objet """
        labels = Label.objects.filter(author=author, name=name.strip().lower())
        if labels.exists():
            for label in labels:
                self.labels.remove(label)
            return True
        return False

    # Métadonnées
    class Meta:
        abstract = True
