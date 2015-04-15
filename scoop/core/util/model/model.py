# coding: utf-8
from __future__ import absolute_import

import operator
import threading
from random import choice, randrange
from time import sleep

from django.db import models
from django.db.transaction import atomic
from django.utils.functional import SimpleLazyObject


class DictUpdateModel:
    """ Mixin de modèle ajoutant une fonction update """

    # Setter
    def update(self, save=False, **kwargs):
        """ Mettre à jour les champs du modèle """
        for (key, value) in kwargs.items():
            setattr(self, key, value)
        if save is True:
            try:
                self.save(update_fields=kwargs.keys())
            except ValueError:  # généralement si un generic field name est employé
                self.save()


@atomic
def resave_queryset(queryset, fields=None, count=None):
    """ Réenregistrer chaque instance du queryset"""

    def _resave_queryset_progress(progress, total):
        """ Afficher la progression pendant la mise à jour du queryset"""
        percent = progress * 100 / total
        print u"{percent:>5.1f}% ({progress})".format(progress=progress, percent=percent)
        sleep(1.0)

    t = None
    total = count or queryset.count()
    criteria = {} if fields is None else {'update_fields': fields}
    for i, instance in enumerate(queryset):
        if t is None or not t.isAlive():
            t = threading.Thread(target=_resave_queryset_progress, args=(i, total))
            t.start()
        instance.save(**criteria)


def get_all_related_objects(instance, limit=2048):
    """ Renvoyer tous les objets liés à une instance """
    # Liste à renvoyer
    result = set()
    # Récupérer les accesseurs qui seront appelés pour récupérer les objets
    links = [rel.get_accessor_name() for rel in instance._meta.get_all_related_objects()]
    # Récupérer les accesseurs, tous les objets des accesseurs, et les ajouter
    for link in links:
        if len(result) > limit:
            break
        try:
            items = getattr(instance, link).all()
            for item in items:
                result.add(item)
        except Exception:
            try:
                result.add(getattr(instance, link))
            except:
                pass
    return result


def search_query(expression, fields, queryset=None):
    """
    Fabriquer une requête de recherche de mots dans plusieurs champs
    On passe une expression avec un ou plusieurs mots
    et une liste de champs texte dans lesquels rechercher.
    La fonction renvoie les paramètres de QuerySet utiles à la recherche.
    Chaque mot de l'expression peut être agrémenté de ! et = en préfixe, afin de
    modifier la requête. Le caractère ! peut aussi se placer en suffixe.
    """
    tokens = expression.split()
    query_groups = []
    for token in tokens:
        query_list = []
        # Variantes de recherche : ^ et $
        if token.startswith('!'):
            matching = 'istartswith'
            token = token[1:]
        elif token.endswith('!'):
            matching = 'iendswith'
            token = token[:-1]
        elif token.startswith('='):
            matching = 'iexact'
            token = token[1:]
        else:
            matching = 'icontains'
        for field in fields:
            # Ajouter une condition de recherche
            query_list.append(models.Q(**{"%s__%s" % (field, matching): token}))
        query_group = reduce(operator.or_, query_list)
        query_groups.append(query_group)
    if queryset is None:
        final_query = reduce(operator.and_, query_groups)
        return final_query
    else:
        for query_group in query_groups:
            queryset = queryset.filter(query_group)
        return queryset


def shuffle_model(self, fields=None):
    """ Suffle les données du modèle, notamment les clés étrangères et clés M2M """
    fields = fields or [self._meta.get_field_by_name(field) for field in set(self._meta.get_all_field_names())]
    for field in fields:
        field = field[0]
        if isinstance(field, models.ForeignKey) and not isinstance(field, models.OneToOneField):
            queryset = field.related.parent_model._default_manager.all()
            queryset = queryset.filter(**field.rel.limit_choices_to).order_by('?')
            if queryset.exists():
                setattr(self, field.name, queryset[0])
        elif isinstance(field, models.ManyToManyField):
            queryset = field.related.parent_model.objects.all().order_by('?')
            queryset = queryset.filter(**field.rel.limit_choices_to)
            if queryset.exists():
                attribute = getattr(self, field.name)
                attribute.clear()
                for i in range(min(randrange(1, 4), queryset.count())):
                    attribute.add(queryset[i])
        elif getattr(field, 'choices', None) is not None:
            choices = list(field.choices)
            if len(choices) > 0:
                setattr(self, field.name, choice(choices)[0])


def limit_to_model_names(*names):
    """ Limit_choices_to via des noms de modèles type app_label.model """
    return reduce(operator.or_, [models.Q(**{'app_label': app, 'model': model}) for app, model in [name.split('.') for name in names]])


def make_lazy_picklable(*args):
    """
    request.user peut être un objet SimpleLazyObject qui ne peut pas être picklé par
    Celery lorsqu'il est dans une autre structure, visiblement.
    Remplacer user par user._wrapped dans ce cas
    :param symbols: normalement, passer locals()
    :param names: normalement, passer les paramètres de la fonction qui sont de type user
    :type names: list[str]
    :type symbols: dict
    """
    return [getattr(arg, '_wrapped', arg) for arg in args]


class SingleDeleteQuerySetMixin(object):
    """ Mixin de queryset implémentant la suppression individuelle des instances du queryset """

    def delete(self):
        """ Supprimer indépendamment chaque objet du queryset """
        for item in self:
            item.delete()


class SingleDeleteQuerySet(models.QuerySet, SingleDeleteQuerySetMixin):
    """ Queryset implémentant la suppression individuelle des instances du queryset """
    pass


class SingleDeleteManager(models.Manager):
    """ Manager implémentant la suppression individuelle des instances du queryset """

    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return SingleDeleteQuerySet(self.model, using=self._db)
