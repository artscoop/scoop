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
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        """ Initialiser le champ """
        super(PipeListField, self).__init__(*args, **kwargs)

    # Getter
    def to_python(self, value):
        """ Renvoyer la valeur python du champ """
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
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        """ Initialiser le champ """
        super(LineListField, self).__init__(*args, **kwargs)

    # Getter
    def to_python(self, value):
        """ Renvoyer la valeur python du champ """
        return OrderedDict(enumerate(value.strip().splitlines() or []))

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
            return image.size
        except IOError:
            return [None, None]

    def _get_image_dimensions(self):
        """ Renvoyer les dimensions de cette image """
        if not hasattr(self, '_dimensions_cache'):
            close = self.closed
            self.open()
            self._dimensions_cache = ImageFieldFile.get_image_dimensions(self, close=close)
        return self._dimensions_cache


class WebImageField(ImageField):
    """ Champ Imagefield n'acceptant que les JPEG, les GIF et les PNG """
    # Configuration
    attr_class = ImageFieldFile
    # Constantes
    ACCEPTED_FORMATS = ('GIF', 'PNG', 'JPEG')
    MINIMUM_DIMENSIONS = (64, 64)

    def __init__(self, *args, **kwargs):
        """ Initialiser le champ """
        self.min_dimensions = list(kwargs.pop('min_dimensions', WebImageField.MINIMUM_DIMENSIONS))
        super(WebImageField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        """ Renvoyer la valeur python des données """
        output = super(WebImageField, self).to_python(data)
        if data is not None:
            # data can be an InMemoryUploadedFile or something else
            if hasattr(data, 'temporary_file_path'):
                fi = data.temporary_file_path()
                print(fi)
            else:
                data.open()  # data est un fichier fermé, il faut l'ouvrir si possible
                fi = BytesIO(data.read() if hasattr(data, 'read') else data['content'])
            # Try to open the filename or file object
            try:
                from PIL import Image
                # Ouvrir l'image
                image = Image.open(fi)
                # If opened, check against Format and dim constraints
                if image.format not in WebImageField.ACCEPTED_FORMATS:
                    raise ValidationError(_("Image not accepted. Accepted formats: {}.").format(', '.join(WebImageField.ACCEPTED_FORMATS)))
                if sorted(image.size) < self.min_dimensions:
                    raise ValidationError(
                        _("Image not accepted. Minimum accepted size is {mw}x{mh}.").format(mw=self.min_dimensions[0], mh=self.min_dimensions[1]))
            except IOError:  # PIL cannot load and handle the image
                raise ValidationError(_("This image cannot be handled. Accepted formats: {}.").format(', '.join(WebImageField.ACCEPTED_FORMATS)))
            except ImportError:  # Maybe an error with PIL only on PyPy
                raise
            # Reset file cursor position if fi is a file object
            if hasattr(fi, 'seek') and callable(fi.seek):
                fi.seek(0)
            return data
        return output
