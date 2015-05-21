# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import TestCase
from testproject.models import Document


class EnvironmentTest(TestCase):
    fixtures = ['documents']

    def test_runner_works(self):
        self.assertTrue(True)

    def test_fixture(self):
        documents = Document.objects.all()
        self.assertEqual(len(documents), 52)
