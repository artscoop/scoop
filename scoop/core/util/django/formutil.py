# coding: utf-8
from __future__ import absolute_import

import os
import tempfile
from collections import OrderedDict
from inspect import isclass
from os.path import join

from django.contrib import messages
from django.db.models.base import Model
from django.forms.forms import Form
from django.forms.models import ModelForm
from django.http.request import QueryDict
from django.http.response import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from scoop.core.templatetags.text_tags import humanize_join
# Choix Oui/Non et Tout
from scoop.core.util.data.typeutil import is_multi_dimensional, make_iterable

CHOICES_NULLBOOLEAN = (('', _(u"All")), (False, _(u"No")), (True, _(u"Yes")))


class ModelFormUtil:
    """
    Mise à jour d'un objet de type Model avec certains champs d'un ModelForm
    - instance : objet dérivé de models.Model
    - form : objet de type forms.ModelForm dont la classe ciblée est celle de instance
    - fieldnames : liste de noms de champs à mettre à jour dans le modèle
    """

    @staticmethod
    def is_field_valid(form, fieldnames):
        """ Renvoyer si un champ d'un formulaire est valide """
        for fieldname in fieldnames:
            # Récupérer le champ
            field = form.fields[fieldname]
            # Récupérer les données du champ et valider
            data = field.widget.value_from_datadict(form.data, form.files, form.add_prefix(fieldname))
            try:
                if not hasattr(form, 'cleaned_data'):
                    form.cleaned_data = {}
                form.cleaned_data[fieldname] = field.clean(data)
                if hasattr(form, 'clean_%s' % fieldname):
                    value = getattr(form, 'clean_%s' % fieldname)()
                    form.cleaned_data[fieldname] = value
            except Exception:
                return False
        return True

    def update_from_form(self, form, fieldnames, save=True, **kwargs):
        """
        Mettre à jour les champs de l'objet selon l'état d'un formulaire
        - La validation ne se fait que sur les champs sélectionnés et valides
        :param fieldnames: itérable contenant le nom des champs à mettre à jour
            Si None, met à jour l'instance via form.save.
        :type fieldnames: list or tuple or set or NoneType
        """
        if isinstance(fieldnames, (list, tuple, set)):
            for fieldname in fieldnames:
                if ModelFormUtil.is_field_valid(form, [fieldname]):
                    setattr(self, fieldname, form.cleaned_data[fieldname])
        elif fieldnames is None:
            self = form.save(commit=False)
        else:
            raise AttributeError(u"You must pass a field names iterable or None.")
        # Terminer en sauvegardant l'objet si demandé
        if save:
            self.update(save=True, **kwargs)
        return self


class Validation(object):
    """ État de validation d'un ou plusieurs formulaires """

    def __init__(self, success=False, code=0, message='', *args, **kwargs):
        """ Initialiser l'objet """
        self.success = success
        self.code = code
        self.message = message

    # Getter
    def is_successful(self):
        """ Renvoyer si la validation a été un succès """
        return bool(self.success)

    def get_code(self):
        """ Renvoyer le code de retour de la validation """
        return self.code


@require_POST
def handle_upload(request):
    """
    Traitement des uploads, Ajax, directs ou fragmentés
    Utilisation :
    - Vous utilisez une vue AJAX qui est appelée pour l'upload progressif
    - Récupérer le résultat de handle_upload dans la vue AJAX
    - Si le résultat est un nom de fichier, l'upload est terminé.
    Vous pouvez ensuite, gérer ce résultat (par exemple) :
      picture.image.save(unidecode(result['name']), File(open(result['path'])))
    """
    # Traiter la requête s'il y a un fichier à remonter
    if request.FILES:
        image_file = request.FILES[request.FILES.keys()[0]]
        image_name = image_file.name if 'name' not in request.POST else request.POST['name']
        # Par défaut, créer ou écrire à la fin du fichier existant
        file_mask = os.O_APPEND | os.O_WRONLY | os.O_CREAT if int(request.POST.get('chunk', 0)) > 0 else os.O_RDWR | os.O_CREAT | os.O_TRUNC
        file_path = join(tempfile.gettempdir(), image_name)  # Chemin dans le répertoire temporaire de l'OS
        # Ouvrir le fichier et écrire les morceaux
        fd = os.open(file_path, file_mask)
        for chunk in image_file.chunks():
            os.write(fd, chunk)
        os.close(fd)
        # Renvoyer le nom du fichier si le dernier chunk a été écrit
        # Ou renvoyer None si la vue appelante ne doit pas effectuer d'action
        if int(request.POST.get('chunk', 0)) + 1 == int(request.POST.get('chunks', 1)):
            return {'path': file_path, 'name': image_name}
        else:
            return HttpResponse()


def has_post(request, action=None):
    """
    Dire si l'objet HttpRequest est en mode POST
    Et contient un paramètre passé (en général le nom de l'action du formulaire')
    """
    posted = (request.method == 'POST')
    if posted and action is not None:
        return posted and (action in request.POST)
    return posted


def _normalize_initial(initial, form):
    """
    Parcourir les données initiales de formulaire et remplacer les instances par les ID etc.
    :type initial: dict
    """

    def convert_value(value):
        """ Convertir une valeur en valeur chaîne ou numérique """
        if isinstance(value, (basestring, int, float, long)):
            return value
        elif isinstance(value, Model):
            return value.pk
        elif isinstance(value, (list, tuple)):
            return [convert_value(item) for item in value]

    output = dict()
    for key, value in initial.items():
        if key in form._meta.fields:
            output[key] = convert_value(value)
    return output


def form(request, config, initial=None):
    """
    Créer un formulaire initialisé selon l'état de la requête.
    Si request contient des données POST, créer le formulaire avec ces données.
    Ex.:
    >> a, b, c = form(request, ((A, None), (B, {'instance': y}), (C, {'instance': z}), initial=None)
    >> a = form(request, {A: {'instance': x}})
    :param config: Configuration des formulaires
    :type config: Form or list[Form] or collections.OrderedDict or tuple[tuple] or dict(len=1) or list[list]
    :param initial: Valeurs des champs par défaut en l'absence de POST
    """
    forms = list()
    config = make_iterable(config, list) if isinstance(config, (ModelForm, Form)) else config
    config = OrderedDict(((item, None) for item in config) if not is_multi_dimensional(config) else config)
    for form_class in config.keys():
        args, kwargs = list(), dict()
        # Réunir les arguments d'initialisation du formulaire
        if request and request.has_post():
            args.append(request.POST)
            args.append(request.FILES)
        elif initial is not None:
            if isinstance(initial, QueryDict):  # Charger des données POST
                args.append(initial.dict())
            else:
                kwargs['initial'] = _normalize_initial(initial, form_class)
        if isclass(form_class) and issubclass(form_class, ModelForm) and config[form_class] is not None:
            kwargs['instance'] = config[form_class]
        # Vérifier que le formulaire fonctionne avec initial
        temp_form = form_class(*args, **kwargs)
        temp_form.request = request
        forms.append(temp_form)
    # Renvoyer les formulaires
    return forms if len(forms) > 1 else forms[0] if forms else None


def are_valid(forms):
    """ Renvoyer si tous les formulaires passés sont valides """
    if not isinstance(forms, list):
        forms = [forms]
    valid = all([form.is_valid() for form in forms])
    return valid


def any_valid(forms):
    """ Renvoyer si un seul des formulaires passés est valide """
    if not isinstance(forms, list):
        forms = [forms]
    valid = any([form.is_valid() for form in forms])
    return valid


def has_valid_changes(form):
    """ Renvoyer si un formulaire est valide a été modifié """
    return form.is_valid() and form.has_changed()


def message_on_invalid(form, request, message, level=None, extra_tags=None):
    """ Afficher un message à l'utilisateur si un formulaire n'est pas valide """
    if not form.is_valid():
        messages.add_message(request, level or messages.SUCCESS, message, extra_tags=extra_tags)


def error_labels(form):
    """ Renvoyer la liste des étiquettes de champs pour les erreurs d'un formulaire """
    if form.errors:
        labels = [field.label for field in form if field.errors]
        return humanize_join(labels, 10, "field;fields")
    return None
