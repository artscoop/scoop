# coding: utf-8
import simplejson

from django.conf import settings
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.shortcuts import import_fullname


@require_POST
def validate_form(request, *args, **kwargs):
    """
    Vue de validation de formulaire (AJAX)
    Valider ou non un formulaire et renvoyer des données AJAX des erreurs
    :param form_classes: classe de formulaire à valider
    :param alias: alias de chemin de classe de settings.FORM_ALIASES
    La validation AJAX frontend se fait via le plugin jQuery.LiveValidation.js
    (se trouve dans static/tool/jQuery/One).
    Le paramètre Django FORM_ALIASES est de la forme :
    - Dictionnaire {alias: [FQN de classes de formulaires]}
    - Dictionnaire {alias: FQN de classe de formulaire}
    """
    # Initialisation
    if kwargs.get('form_classes', False):
        Forms = kwargs['form_classes']
    elif kwargs.get('alias', False):
        alias, aliases = kwargs.get('alias'), getattr(settings, 'FORM_ALIASES', dict())
        form_names = make_iterable(aliases.get(alias))
        Forms = [import_fullname(form_name) for form_name in form_names if '.' in form_name]
    else:
        return HttpResponseBadRequest("You need to send a form or a form alias")
    output = {'valid': True, '_all_': []}
    # Vérifier la validité de tous les formulaires passés
    Forms = make_iterable(Forms)
    for Form in Forms:
        form = Form(request.POST, request.FILES)
        # Vérifier la validité du formulaire
        if form.is_valid() is False:
            output['_all_'].append(form.non_field_errors())
            output['valid'] = False
            field_names = form.fields.keys()
            for field_name in field_names:
                auto_id = form[field_name].auto_id
                output[auto_id] = form[field_name].errors
    return HttpResponse(simplejson.dumps(output))
