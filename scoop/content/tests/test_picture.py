# coding: utf-8
from __future__ import absolute_import

from django.test import TestCase

from scoop.content.models.picture import Picture
from scoop.user.models.user import User


class PictureTest(TestCase):
    """ Test des images """
    # Configuration
    fixtures = ['mailtype', 'options']
    urls = 'settings.urlconf.base'

    def setUp(self):
        """ Définir l'environnement de test """
        self.user = User.objects.create(username='pictureuser', email='foo@foobar3.foo')
        # Créer des images, une via Google Search, et une par URL
        self.picture1 = Picture.objects.create_from_uri("find://flower?id=0", author=self.user, title="Flower")
        self.picture2 = Picture.objects.create_from_uri("http://media.topito.com/wp-content/uploads/2014/10/95qHQgg.gif", author=self.user, title="Nyan")

    def tearDown(self):
        """ Nettoyer l'environnement des tests """
        for picture in Picture.objects.all():
            picture.delete(clear=True)

    def test_picture(self):
        """ Tester l'état des images téléchargées """
        self.assertIsNotNone(self.picture2, "picture 2 should not be None")
        self.assertIsNone(self.picture1.moderated, "picture 1 was moderated but should not by default")
        self.assertGreater(self.picture1.get_file_size(raw=True), 1800, "the downloaded picture should be bigger than 1800 bytes")
        self.assertTrue(self.picture2.get_animations().count() > 0, "the downloaded picture should have animations attached")
        self.assertTrue(self.picture2.animated is True, "the downloaded picture should have the animated attribute set to True")
        self.assertTrue(self.picture2.get_extension() == '.jpg', "the downloaded picture should have been converted to a jpg still")
        self.assertGreater(self.picture2.get_animation_duration(), 0.1, "the picture animations should last longer than 0.1 seconds")
        self.assertFalse('screen' in self.picture2.get_filename(), "the picture has been created from scratch, this is not normal")
