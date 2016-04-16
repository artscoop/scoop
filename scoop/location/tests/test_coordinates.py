# coding: utf-8

from django.contrib.gis.db.models.functions import Distance
from django.test import TestCase

from scoop.location.models.position import Position
from scoop.user.models.user import User


class CoordinatesTest(TestCase):
    """ Test des coordonnées géographiques  """
    fixtures = []

    def setUp(self):
        """ Préparer l'environnement de test """
        pass

    # Tests
    def test_coordinates(self):
        """ Tester les coordonnées """
        user1 = User.objects.create(username='anita', email='anita@foobar.foo')
        user2 = User.objects.create(username='benny', email='benny@foobar.foo')
        user3 = User.objects.create(username='carla', email='carla@foobar.foo')
        position1 = Position.objects.set_position(user1, 0.0, 0.0)
        position2 = Position.objects.set_position(user2, 0.0, 2.0)  # Est
        position3 = Position.objects.set_position(user3, 1.0, 0.0)  # Nord

        self.assertEqual(position1.get_cardinal_position(position2, 'tick'), 0)  # est
        self.assertEqual(position1.get_cardinal_position(position3, 'tick'), 4)  # nord
        self.assertEqual(position3.get_cardinal_position(position1, 'tick'), 12)  # sud

        self.assertEqual(position1.get_formatted_coordinates(), "↑:0.0000 →:0.0000")
        self.assertEqual(position1.get_sexagesimal_coordinates(), "0°0ʹ0.000ʺ N, 0°0ʹ0.000ʺ E")

        # Tester que le tri par distance fonctionne
        queryset = Position.objects.all().annotate(distance=Distance('position', position1.position)).order_by('distance')
        self.assertEqual(list(queryset), [position1, position3, position2])

        # Tester les propriétés
        position1.point = (1.0, 1.0)
        position1.save()
        self.assertEqual(position1.point, (1.0, 1.0))
        self.assertNotEqual(position1.point, (0.0, 0.0))
