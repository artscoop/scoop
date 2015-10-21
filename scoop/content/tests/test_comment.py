# coding: utf-8
from __future__ import absolute_import

import loremipsum
from django.conf import settings
from django.db.models.base import Model
from django.test import TestCase
from django.utils.importlib import import_module

from scoop.content.models.comment import Comment
from scoop.content.models.content import Content
from scoop.user.models.user import User


class CommentTest(TestCase):
    """ Test des commentaires """
    # Configuration
    fixtures = ['category', 'mailtype', 'options']

    @classmethod
    def setUp(self):
        """ Définir l'environnement de test """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user = User.objects.create(username='commentuser', email='foo@foobar1.foo')
        self.user.set_password('commentuser')
        self.user.save()
        # Créer des contenus commentables ou pas
        self.content1 = Content.objects.create([self.user], 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(8), visible=True, commentable=True)
        self.content2 = Content.objects.create([self.user], 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(8), visible=True, commentable=False)
        # Commenter l'utilisateur et tester l'état des commentaires
        self.comment1 = Comment.objects.comment(None, self.user, self.user, "Commentaire 1", force=True)
        self.comment2 = Comment.objects.comment(None, self.user, self.user, "Commentaire 2", force=True)
        self.comment3 = Comment.objects.comment(None, self.user, self.user, "Commentaire 3", force=True)
        self.comment4 = Comment.objects.comment(None, self.user, self.user, "Commentaire 4", force=True)
        self.comment5 = Comment.objects.comment(None, self.user, self.user, "Commentaire 5")  # échec : user n'est pas un commentablemodel et force == False
        self.comment6 = Comment.objects.comment(None, self.user, self.content1, "Commentaire 6")
        self.comment7 = Comment.objects.comment(None, self.user, self.content2, "Commentaire 7")  # échec : content.commentable == False

    def test_commentability(self):
        """ Tester que les commentaires ont été créés ou non """
        self.assertIsNotNone(self.comment1, "this comment should be created")
        self.assertIsNotNone(self.comment2, "this comment should be created")
        self.assertIsNotNone(self.comment3, "this comment should be created")
        self.assertIsNotNone(self.comment4, "this comment should be created")
        self.assertIsNotNone(self.comment6, "this comment should be created")
        self.assertIsNone(self.comment5, "this comment should be none")
        self.assertIsNone(self.comment7, "this comment should be none")

    def test_comment_status(self):
        """ Test properties of comments """
        self.assertEqual(self.comment1.get_name(), self.user.get_short_name(), "comment's name should be {0}, is {1} instead".format(self.user.get_short_name(), self.comment1.get_name()))
