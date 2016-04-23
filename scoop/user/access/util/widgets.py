# coding: utf-8
from django import forms
from IPy import IP


class IPIntegerField(forms.IntegerField):
    """ Champ de saisie d'IP. Accepte n'importe quel format d'IP, le stocke en long """

    def to_python(self, value):
        """ Conversion de la saisie en valeur python """
        try:
            value = IP(value).int()
        except Exception:
            value = 0
        return value

    def prepare_value(self, value):
        """ Conversion d'une valeur python en valeur chaîne """
        try:
            return IP(str(value)).__str__()
        except:
            return ""
