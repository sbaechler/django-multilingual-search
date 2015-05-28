# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import SimpleTestCase

from haystack.query import SearchQuerySet
from multilingual.elasticsearch_backend import ElasticsearchMultilingualSearchQuery


class BackendTest(SimpleTestCase):
    maxDiff = None

    def test_live_query(self):
        sqs = SearchQuerySet()
        self.assertFalse(sqs.query.has_run())
        self.assertIsInstance(sqs.query, ElasticsearchMultilingualSearchQuery)
        all_results = sqs.all()
        list(all_results)
