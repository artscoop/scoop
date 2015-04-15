# coding: utf-8
from __future__ import absolute_import

import urllib2
from decimal import Decimal, DivisionByZero

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from scoop.core.util.model.model import SingleDeleteManager


class CurrencyManager(SingleDeleteManager):
    """ Manager des devises """

    # Getter
    def get_by_natural_key(self, name):
        """ Renvoyer une devise par clé naturelle """
        return self.get(short_name=name)

    # Setter
    def update_balances(self, names=None):
        """ Mettre à jour le cours des devises """
        try:
            for currency in (self.all() if names is None else self.filter(short_name__in=names)):
                currency.update_balance()
            return True
        except:
            return False


class Currency(models.Model):
    """ Devise """
    # Champs
    name = models.CharField(max_length=32, blank=False, verbose_name=_(u"Name"))
    short_name = models.CharField(max_length=6, blank=False, unique=True, verbose_name=_(u"3 letter name"))
    balance = models.DecimalField(max_digits=10, decimal_places=7, default=-1, verbose_name=pgettext_lazy('currency', u"Quote"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('currency', u"Updated"))
    objects = CurrencyManager()

    # Getter
    def natural_key(self):
        """ Renvoyer la clé naturelle de la devise """
        return (self.short_name,)

    def get_amount(self, currency='USD', amount=1.0):
        """ Convertir un montant de cette devise vers une autre """
        try:
            if not isinstance(currency, Currency):
                try:
                    currency = Currency.objects.get(short_name=currency)
                except:
                    pass
            return amount * (self.balance / currency.balance)
        except DivisionByZero:
            return None

    # Setter
    def update_balance(self, save=True):
        """ Mettre à jour les valeurs de la devise """
        try:
            req = urllib2.urlopen('http://quote.yahoo.com/d/quotes.csv?s={}USD=X&f=l1&e=.csv'.format(self.short_name))
            result = req.read()
        except:
            result = 0
        self.balance = Decimal(result)
        if save is True:
            self.save()

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.balance == -1:
            self.update_balance(save=False)
        super(Currency, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _(u"currency")
        verbose_name_plural = _(u"currencies")
        app_label = 'location'
