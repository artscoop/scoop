# coding: utf-8
import os
from os.path import join

from django.test import TestCase
from scoop.content.models.picture import Picture
from scoop.user.models.user import User

path = os.path.dirname(__file__)


class PictureTest(TestCase):
    """ Test des images """

    # Configuration
    fixtures = ['mailtype', 'options']
    urls = 'settings.urlconf.base'

    def setUp(self):
        """ Définir l'environnement de test """
        self.user = User.objects.create(username='pictureuser', email='foo@foobar3.foo')

    def tearDown(self):
        """ Nettoyer l'environnement des tests """
        for picture in Picture.objects.all():
            picture.delete(clear=True)

    def test_picture(self):
        """ Tester l'état des images téléchargées """
        # Créer des images, une via Google Search, et une par URL
        picture1 = Picture.objects.create_from_uri("find://flower?id=0", author=self.user, title="Flower")
        picture2 = Picture.objects.create_from_file(join(path, 'images', 'banana.gif'), author=self.user, title="Banana")
        self.assertIsNotNone(picture2, "picture 2 should not be None")
        self.assertIsNone(picture1.moderated, "picture 1 was moderated but should not by default")
        self.assertGreater(picture1.get_file_size(raw=True), 1800, "the downloaded picture should be bigger than 1800 bytes")
        self.assertTrue(picture2.get_animations().count() > 0, "the downloaded picture should have animations attached")
        self.assertTrue(picture2.animated is True, "the downloaded picture should have the animated attribute set to True")
        self.assertTrue(picture2.get_extension() == '.jpg', "the downloaded picture should have been converted to a jpg still")
        self.assertGreater(picture2.get_animation_duration(), 0.1, "the picture animations should last longer than 0.1 seconds")
        self.assertFalse('screen' in picture2.get_filename(), "the picture has been created from scratch, this is not normal")

    def test_autocrop(self):
        """ Tester le fonctionnement du rognage automatique avec et sans OpenCV """
        # Tester les dimensions de l'image par défaut
        picture1 = Picture.objects.create_from_file(join(path, 'images', 'croppable.jpg'), author=self.user, title='croppable picture')
        self.assertTrue(picture1.exists(), "the loaded picture should work and be accessible")
        self.assertEqual(picture1.get_dimension(), (545, 310), "the picture should be 545x310 by default")
        # Tester les dimensions de l'image rognée autour de la zone importante
        picture2 = picture1.clone()
        picture2.autocrop_feature_detection()
        self.assertLess(picture2.height, 200, "the picture should be cropped by more than 48 pixels vertically")
        self.assertGreater(picture2.height, 160, "the picture viable content is more than 160 pixels high")
        # Tester les dimensions de l'image rognée par couleur de bordure
        picture3 = picture1.clone()
        picture3.autocrop()
        self.assertGreater(picture3.height, 262, "the picture should be cropped by not many pixels vertically")

    def test_markers(self):
        """ Tester l'écriture et la lecture de marqueurs """
        picture1 = Picture.objects.create_from_file(join(path, 'images', 'croppable.jpg'), author=self.user, title='marked picture')
        picture1.set_marker('x,18,violence')
        self.assertEqual(picture1.get_markers(), ['x', '18', 'violence'], "the picture markers should be in order x, 18 ans violence")
        self.assertTrue(picture1.has_marker('18'), "the picture should have a marker named 18")

    def test_license(self):
        """ Tester l'écriture et la lecture de licence/auteur """
        picture1 = Picture.objects.create_from_file(join(path, 'images', 'croppable.jpg'), author=self.user, title='marked picture')
        picture1.set_license(1, "Robert Doisneau")
        self.assertEqual(picture1.get_license_id(), 1)
        self.assertEqual(picture1.get_license_name().lower(), 'copyright')
        self.assertEqual(picture1.get_license_creator(), 'Robert Doisneau')
