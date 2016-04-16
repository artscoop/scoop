# coding: utf-8
from django.views.generic.base import TemplateView

from scoop.core.models.optiongroup import OptionGroup


class OptionSheetView(TemplateView):
    """ Vue de cheat-sheet des options """
    template_name = 'core/view/option-sheet.html'

    def get_context_data(self, **kwargs):
        """ Renvoyer le contexte de rendu du template """
        return {'groups': OptionGroup.objects.all()}
