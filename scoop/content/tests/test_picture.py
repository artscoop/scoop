# coding: utf-8
import os
import cv2
from os.path import join

from django.test import TestCase
from scoop.content.models.picture import Picture
from scoop.core.util.stream.directory import Paths
from scoop.user.models.user import User


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
        picture2 = Picture.objects.create_from_file(join(Paths.get_root_dir('isolated', 'static', 'assets', 'tests', 'content'), 'banana.gif'), author=self.user, title="Banana")
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
        path = os.path.dirname(__file__)
        picture1 = Picture.objects.create_from_file(join(path, 'images', 'croppable.jpg'), author=self.user, title='croppable picture')
        self.assertTrue(picture1.exists(), "the loaded picture should work and be accessible")
        self.assertEqual(picture1.get_dimension(), (545, 310), "the picture should be 545x310 by default")

        picture2 = picture1.clone()
        picture2.autocrop_feature_detection()
        self.assertLess(picture2.height, 200, "the picture should be cropped by more than 48 pixels vertically")
        self.assertGreater(picture2.height, 160, "the picture viable content is more than 160 pixels high")

        picture3 = picture1.clone()
        picture3.autocrop()
        self.assertGreater(picture3.height, 262, "the picture should be cropped by not many pixels vertically")
