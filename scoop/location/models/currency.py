# coding: utf-8
from datetime import timedelta
from decimal import Decimal, DivisionByZero

import requests

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.util.model.model import SingleDeleteManager


class CurrencyManager(SingleDeleteManager):
    """ Manager des devises """

    # Getter
    def get_by_natural_key(self, name):
        """ Renvoyer une devise par clé naturelle """
        return self.get(short_name=name)

    def name_exists(self, name):
        """
        Renvoyer si une devise avec le nom passé est connue

        :param name: nom de devise, ex. USD ou US Dollar
        """
        return self.filter(Q(short_name__iexact=name) | Q(name__iexact=name)).exists()

    def get_amount(self, amount, source, destination):
        """
        Renvoyer la conversion de amount source en destination

        ex. Renvoyer la conversion de 15 EUR en USD
        :param amount: montant
        :param source: devise source, ex. USD, EUR, JPY ou Euro
        :param destination: devise de destination, ex. USD, AUD
        :raises: models.DoesNotExist si la devise n'existe pas
        """
        try:
            source_currency = self.get(Q(short_name__iexact=source) | Q(name__iexact=source))
            return source_currency.get_amount(destination, amount)
        except Currency.DoesNotExist:
            return None

    # Setter
    def update_balances(self, names=None):
        """
        Mettre à jour le cours des devises

        La méthode ne met à jour que les devises n'ayant pas été mises à jour dans les
        48 dernières heures, ou n'ayant pas de cours valide.
        """
        try:
            update_limit = timezone.now() - timedelta(days=2)
            base_queryset = self.filter(Q(updated__gt=update_limit) | Q(balance=-1))
            for currency in (base_queryset if names is None else base_queryset.filter(short_name__in=names)):
                currency.update_balance()
            return True
        except ValueError:
            return False


class Currency(models.Model):
    """ Devise """

    # Champs
    name = models.CharField(max_length=32, blank=False, verbose_name=_("Name"))
    symbol = models.CharField(max_length=4, blank=True, verbose_name=_("Symbol"))
    short_name = models.CharField(max_length=6, blank=False, primary_key=True, verbose_name=_("3 letter name"))
    balance = models.DecimalField(max_digits=12, decimal_places=8, default=-1, verbose_name=pgettext_lazy('currency', "Quote"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('currency', "Updated"))
    objects = CurrencyManager()

    # Getter
    def natural_key(self):
        """ Renvoyer la clé naturelle de la devise """
        return self.short_name,

    def get_amount(self, currency='USD', amount=1.0):
        """ Convertir un montant de cette devise vers une autre """
        try:
            if not isinstance(currency, Currency):
                try:
                    currency = Currency.objects.get(short_name=currency)
                except Currency.DoesNotExist:
                    pass
            return amount * (self.balance / currency.balance)
        except DivisionByZero:
            return None

    # Setter
    def update_balance(self, save=True):
        """ Mettre à jour les valeurs de la devise """
        try:
            resource = requests.get('http://quote.yahoo.com/d/quotes.csv?s={}USD=X&f=l1&e=.csv'.format(self.short_name))
            result = resource.text
            self.balance = Decimal(float(result))
        except (OSError, ValueError):
            result = 0
        if save is True:
            self.save()

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.balance == -1:
            self.update_balance(save=False)
        super(Currency, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("currency")
        verbose_name_plural = _("currencies")
        app_label = 'location'
