# coding: utf-8
from __future__ import absolute_import


def first_visit(request):
    """ Ajouter au contexte FIRST_VISIT si l'utilisateur est inconnu """
    if not request.user or not request.user.is_authenticated():
        if not request.session.get('is_known', False):
            return {'FIRST_VISIT': True}
        request.session['is_known'] = True
