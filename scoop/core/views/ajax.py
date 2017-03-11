# coding: utf-8
import simplejson

from django.conf import settings
from django.forms.models import ModelForm
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.shortcuts import import_qualified_name


@require_POST
def validate_form(request, form_classes=None, alias=None):
    """
    Vue de validation de formulaire (AJAX)

    Valider ou non un formulaire et renvoyer des données AJAX des erreurs
    :param request: Requête HTTP (WSGI)
    :param form_classes: classe de formulaire à valider
    :param alias: alias de classes de formulaire (voir settings.FORM_ALIASES)
    La validation AJAX frontend se fait via le plugin jQuery.LiveValidation.js
    (se trouve dans static/tool/jQuery/One). La page appelle liveValidate sur un
    élément formulaire.
    Le paramètre settings.FORM_ALIASES est de la forme :
    - Dictionnaire {alias: [FQN de classes de formulaires]}
    - Dictionnaire {alias: FQN de classe de formulaire}

    Le formulaire peut, et devrait, contenir un champ nommé "id",
    dont la valeur est celle de l'objet en cours d'édition si applicable.
    Ce champ id est utilisé pour initialiser correctement le formulaire
    à valider. Les configurations avec plusieurs id (un id par formulaire)
    ne sont pas encore prises en charge.

    :returns: Des données au format JSON. La clé 'valid' indique si la validation
        s'est faite correctement. Si la valeur de 'valid' est False, alors d'autres
        clés contiendront des données d'erreur. La clé '_all_' est une liste
        contenant les erreurs générales de validation. Les autres clés sont
        les id des champs qui ont provoqué l'échec de la validation, leur valeur
        contient le message d'erreur
    """

    # Initialisation
    if form_classes:
        forms = form_classes
    elif alias:
        aliases = getattr(settings, 'FORM_ALIASES', dict())
        form_names = make_iterable(aliases.get(alias))
        forms = [import_qualified_name(form_name) for form_name in form_names if '.' in form_name]
    else:
        return HttpResponseBadRequest("You need to send a form or a form alias")
    # Vérifier la validité de tous les formulaires passés
    forms = make_iterable(forms)
    id_passed = request.POST.get('id')  # Nécessite un champ hidden nommé "id"
    output = {'valid': True, '_all_': []}
    for form in forms:
        extra = dict()
        if id_passed and issubclass(form, ModelForm):  # Ne pas utiliser d'attribut instance pour les non ModelForm
            klass = form._meta.model
            extra = {'instance': klass.objects.get(id=id_passed)}  # Nécessaire pour l'édition de modèle
        form = form(request.POST, request.FILES, **extra)
        # Vérifier la validité du formulaire
        if not form.is_valid():
            output['_all_'].append(form.non_field_errors())
            output['valid'] = False
            field_names = form.fields.keys()
            for field_name in field_names:
                auto_id = form[field_name].auto_id
                output[auto_id] = form[field_name].errors
    return HttpResponse(simplejson.dumps(output))
