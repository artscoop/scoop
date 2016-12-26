# coding: utf-8
from collections import OrderedDict
from io import BytesIO

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.files import FieldFile, ImageField
from django.utils.translation import ugettext_lazy as _


class PipeListField(models.TextField):
    """ Champ liste séparée par des pipes (|) """
    description = _("Pipe separated values of same type")

    def __init__(self, *args, **kwargs):
        """ Initialiser le champ """
        super(PipeListField, self).__init__(*args, **kwargs)

    # Getter
    def to_python(self, value):
        """ Renvoyer la valeur python du champ """
        return value.split("|")

    def from_db_value(self, value, expression, connection, context):
        """ Renvoyer la valeur python depuis la valeur de la db """
        return value.split("|")

    def get_prep_value(self, value):
        """ Renvoyer la valeur en base de données du champ """
        return "|".join(value)

    def formfield(self, **kwargs):
        """ Renvoyer le champ utilisé """
        return super(PipeListField, self).formfield(**kwargs)

    def get_internal_type(self):
        """ Renvoyer le type de champ interne """
        return 'TextField'

    def value_to_string(self, obj):
        """ Renvoyer une représentation texte de la valeur du champ """
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class LineListField(models.TextField):
    """ Champ liste/dictionnaire à index 0 séparé par des retours chariot """
    description = _("Line separated text values")

    def __init__(self, *args, **kwargs):
        """ Initialiser le champ """
        super(LineListField, self).__init__(*args, **kwargs)

    # Getter
    def to_python(self, value):
        """ Renvoyer la valeur python du champ """
        return OrderedDict(enumerate(value.strip().splitlines() or []))

    def from_db_value(self, value, expression, connection, context):
        """ Renvoyer la valeur python depuis la valeur de la db """
        return self.to_python(value)

    def get_prep_value(self, value):
        """ Renvoyer la valeur en DB du champ """
        if isinstance(value, dict):
            return "\n".join(value.values())
        return _("Yes\nNo")

    def formfield(self, **kwargs):
        """ Renvoyer le type de champ de formulaire """
        return super(LineListField, self).formfield(**kwargs)

    def get_internal_type(self):
        """ Renvoyer le type interne du champ """
        return 'TextField'

    def value_to_string(self, obj):
        """ Renvoyer une représentation chaîne de la valeur de l'objet """
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class ImageFieldFile(FieldFile):
    """ Champ fichier pour WebImageField """

    def delete(self, save=True):
        """ Supprimer """
        # Clear the image dimensions cache
        if hasattr(self, '_dimensions_cache'):
            del self._dimensions_cache
        super(ImageFieldFile, self).delete(save)

    def _get_width(self):
        """ Renvoyer la largeur de l'image """
        dimensions = self._get_image_dimensions()
        return dimensions[0] if dimensions else None

    def _get_height(self):
        """ Renvoyer la hauteur de l'image """
        dimensions = self._get_image_dimensions()
        return dimensions[1] if dimensions else 0

    # Propriétés
    width = property(_get_width)
    height = property(_get_height)

    @staticmethod
    def get_image_dimensions(file_or_path, close=False):
        """ Renvoyer les dimensions d'une image """
        try:
            from PIL import Image
            # Ouvrir l'image
            image = Image.open(file_or_path)
            size = image.size
            image.close()
            return size
        except IOError:
            return [None, None]

    def _get_image_dimensions(self):
        """ Renvoyer les dimensions de cette image """
        try:
            if not hasattr(self, '_dimensions_cache'):
                close = self.closed
                self.open()
                self._dimensions_cache = ImageFieldFile.get_image_dimensions(self, close=close)
                self.close()
            return self._dimensions_cache
        except FileNotFoundError:
            return [None, None]


class WebImageField(ImageField):
    """ Champ Imagefield n'acceptant que les JPEG, les GIF et les PNG """

    # Constantes
    ACCEPTED_FORMATS = ('GIF', 'PNG', 'JPEG')
    MINIMUM_DIMENSIONS = (64, 64)

    def __init__(self, *args, **kwargs):
        """ Initialiser le champ """
        self.min_dimensions = list(kwargs.pop('min_dimensions', WebImageField.MINIMUM_DIMENSIONS))
        super(WebImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """ Renvoyer la valeur python des données """
        data = super().clean(*args, **kwargs)
        image = data.file.image
        width, height = data.width, data.height
        if image.format not in WebImageField.ACCEPTED_FORMATS:
            raise ValidationError(_("Image not accepted. Accepted formats: {}.").format(', '.join(WebImageField.ACCEPTED_FORMATS)))
        if width < self.min_dimensions[0] or height < self.min_dimensions[1]:
            raise ValidationError(
                _("Image not accepted. Minimum accepted size is {mw}x{mh}, got {iw}x{ih}").format(
                    mw=self.min_dimensions[0], mh=self.min_dimensions[1], iw=width, ih=height))
        return data
