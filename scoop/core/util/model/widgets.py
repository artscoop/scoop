# coding: utf-8
import datetime
import itertools
import math
import re
from itertools import chain

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from django.forms.widgets import CheckboxInput, CheckboxSelectMultiple
from django.utils import datetime_safe
from django.utils.formats import get_format
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from floppyforms.widgets import SelectDateWidget as SelectDateWidgetBase

# Constantes
RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')


def _parse_date_fmt():
    """
    Parcourir le format actuel de dates
    Renvoyer un tableau de 'day','month' et 'year' selon le format
    """
    fmt = get_format('DATE_FORMAT')
    escaped = False
    output = []
    for char in fmt:
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif char in 'Yy':
            output.append('year')
        elif char in 'bEFMmNn':
            output.append('month')
        elif char in 'dj':
            output.append('day')
    return output


class SelectDateWidget(SelectDateWidgetBase):
    """
    Remix du SelectDateWidget de Floppyforms
    Contrôle affichant trois <selectbox>
    Propose la correction automatique de la date.
    Ex. 31 février devient 28 ou 29 selon que la date est valide.
    Lorsque l'utilisateur soumet une date invalide, plutôt que de réinitialiser les champs à 0,
    prendre la date inférieure la plus proche valide.
    """
    # Constantes
    none_value = (0, '---')
    month_field, day_field, year_field = '%s_month', '%s_day', '%s_year'
    template_name = 'floppyforms/select_date.html'

    def value_from_datadict(self, data, files, name):
        """ Renvoyer la valeur de type "python" pour l'état du widget """
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if y == m == d == "0":
            return None
        if y and m and d:
            if settings.USE_L10N:
                input_format = get_format('DATE_INPUT_FORMATS')[0]
                date_value = None
                try:
                    date_value = datetime.date(int(y), int(m), int(d))
                except ValueError:
                    day = int(d)
                    while True:
                        try:
                            day = day - 1
                            date_value = datetime.date(int(y), int(m), day)
                        except:
                            continue
                        break
                    return date_value
                else:
                    date_value = datetime_safe.new_date(date_value)
                    return date_value.strftime(input_format)
            else:
                return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)


class SimpleCheckboxSelectMultiple(CheckboxSelectMultiple):
    """
    Contrôle Multiselect, affichant les éléments checkbox en listes
    à puces, et affichant les cases à cocher à gauche de leur label
    """

    def render(self, name, value, attrs=None, choices=()):
        """ Rendre le widget """
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<ul>']
        # Normalize to strings
        str_values = set([str(v) for v in value])
        for i, (option_value, option_label) in enumerate(itertools.chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='{}_{}'.format(attrs['id'], i))
                label_for = ' for="{}"'.format(final_attrs['id'])
            else:
                label_for = ''
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = str(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(str(option_label))
            output.append('<li>{} <label{}>{}</label></li>'.format(rendered_cb, label_for, option_label))
        output.append('</ul>')
        return mark_safe('\n'.join(output))


class ColumnCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Contrôle Multiselect affichant les choix en plusieurs colonnes
    Chaque colonne est contenue dans un <ul>.
    Le constructeur accepte columns et css_class
    """

    def __init__(self, columns=2, css_class=None, **kwargs):
        """ Initialiser le widget """
        super(self.__class__, self).__init__(**kwargs)
        self.columns = columns
        self.css_class = css_class

    def render(self, name, value, attrs=None, choices=()):
        """ Rendre le widget """
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        choices_enum = list(enumerate(chain(self.choices, choices)))
        # This is the part that splits the choices into columns.
        # Slices vertically.  Could be changed to slice horizontally, etc.
        column_sizes = columnize(len(choices_enum), self.columns)
        columns = []
        for column_size in column_sizes:
            columns.append(choices_enum[:column_size])
            choices_enum = choices_enum[column_size:]
        output = []
        for column in columns:
            if self.css_class:
                output.append('<ul class="%s"' % self.css_class)
            else:
                output.append('<ul>')
            # Normalize to strings
            str_values = set([str(v) for v in value])
            for i, (option_value, option_label) in column:
                # If an ID attribute was given, add a numeric index as a suffix,
                # so that the checkboxes don't all have the same ID attribute.
                if has_id:
                    final_attrs = dict(final_attrs, id='%s_%s' % (
                        attrs['id'], i))
                    label_for = ' for="%s"' % final_attrs['id']
                else:
                    label_for = ''

                cb = forms.CheckboxInput(final_attrs, check_test=lambda v: v in str_values)
                option_value = str(option_value)
                rendered_cb = cb.render(name, option_value)
                option_label = conditional_escape(str(option_label))
                output.append('<li><label%s>%s %s</label></li>' % (
                    label_for, rendered_cb, option_label))
            output.append('</ul>')
        return mark_safe('\n'.join(output))


def columnize(items, columns):
    """
    Calculer le nombre d'éléments par colonne avec n éléments et m colonnes.
    La fonction renvoie une liste, de longueur égale au nombre de colonnes,
    et indiquant à chaque indice le nombre d'éléments dans la colonne.
    ex. columnize(7,4) = [2,2,2,1] et columnize(10,2) = [5,5]
    """
    items_per_column = []
    for _dummy in range(columns):
        col_size = int(math.ceil(float(items) / columns))
        items_per_column.append(col_size)
        items -= col_size
        columns -= 1
    return items_per_column


class AdminSplitDateTime(forms.SplitDateTimeWidget):
    """
    Contrôle repris du champ Datetime de l'admin, mais affichant les labels
    avec du markup HTML afin de pouvoir appliquer une mise en forme
    """

    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe('<p class="datetime"><span class="vDateTimeLabel">%s</span> %s<br /><span class="vDateTimeLabel">%s</span> %s</p>' %
                         (_('Date'), rendered_widgets[0], _('Time'), rendered_widgets[1]))
