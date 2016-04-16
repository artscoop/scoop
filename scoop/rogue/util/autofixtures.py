# coding: utf-8
import random

from autofixture import AutoFixture, register
from autofixture.generators import LoremSentenceGenerator
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import ContentType

from scoop.rogue.models import FlagType
from scoop.rogue.models.flag import Flag


# Générateurs
# Utilisateur
def values_user():
    return get_user_model().objects.all().order_by('?')[0]


# Id
def values_user_id():
    return get_user_model().objects.all().order_by('?')[0].id


# Type de contenu ciblé
def values_content_type():
    return ContentType.objects.get(model="user", app_label="user")


# Flag type
def values_type():
    return FlagType.objects.filter(content_type__model="user").order_by('?')[0]


# Statut
def values_status():
    return random.choice([0, 1, 2, 3, 4, 5, 6])


# Booléen
def values_bool():
    return random.choice([True, False])


# Pourcentage
def values_percent():
    return random.choice(range(0, 101))


class FlagAutoFixture(AutoFixture):
    """ Fixture automatique de signalements """
    generate_fk = False
    generate_m2m = False
    follow_fk = True
    follow_m2m = False
    field_values = {
        'details': LoremSentenceGenerator(max_length=32),
        'url': "",
        'name': "",
        'content_type': values_content_type,
        'object_id': values_user_id,
        'author': values_user,
        'type': values_type,
        'status': values_status,
        'automatic': values_bool,
        'priority': values_percent,
    }


# Enregistrer la classe de Fixture
register(Flag, FlagAutoFixture)
