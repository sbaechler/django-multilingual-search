# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import TestCase
from django.utils import translation
from django.utils.html import escape
import haystack
from haystack.query import SearchQuerySet
import time

from testproject.models import Document
from unittests.mocks import Data

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2

from multilingual.elasticsearch_backend import ElasticsearchMultilingualSearchQuery, \
    ElasticsearchMultilingualSearchEngine


class BackendTest(TestCase):
    fixtures = ['small']
    maxDiff = None
    index_exists = False

    def setUp(self):
        self.count = 3
        haystack.connections.reload('default')

    def tearDown(self):
        if self.index_exists:
            engine = ElasticsearchMultilingualSearchEngine()
            es = engine.backend('default', **Data.connection_options)
            es.clear(commit=True)
            time.sleep(1)

    def test_live_query(self):
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.setup()
        sqs = SearchQuerySet()
        self.assertFalse(sqs.query.has_run())
        self.assertIsInstance(sqs.query, ElasticsearchMultilingualSearchQuery)
        all_results = sqs.all()
        self.assertEqual(list(all_results), [])  # execute a query
        self.assertTrue(isinstance(all_results, SearchQuerySet))

    def test_query_method(self):
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.setup()
        # fill up the index
        self.index_exists = True
        unified_index = engine.get_unified_index()
        index = unified_index.get_index(Document)
        iterable = Document.objects.all()
        es.update(index, iterable)
        time.sleep(1)
        id = 'testproject.document.2'
        i = 0
        # use this document as a reference.
        reference = Document.objects.get(id=2)

        for language in es.languages:
            # check all language indexes
            index_name = es._index_name_for_language(language)
            self.assertTrue(es.conn.indices.exists(index_name))
            count = es.conn.count(index=index_name)
            self.assertEqual(self.count, count['count'])

            # make sure the index has been created
            while not es.conn.exists(index=index_name, id=id) and i < 5:
                time.sleep(0.5)
                i += 1
            self.assertTrue(es.conn.exists(index=index_name, id=id))
            # get the document with the above id from the correct index
            doc = es.conn.get(index=index_name, id=id)
            self.assertTrue(doc['found'])
            self.assertEqual(doc['_type'], 'modelresult')
            self.assertEqual(doc['_source']['docid'], reference.docid)
            with translation.override(language):
                self.assertIn(escape(reference.text), doc['_source']['text'])

        with translation.override('en'):
            # test the search queryset
            sqs = SearchQuerySet()
            # Django 1.5 doesn't clean up patches
            self.assertFalse(isinstance(sqs.query.backend.conn, mock.Mock))
            result = sqs.filter(content='United States')
            # result might be empty the first time this is called. (Django < 1.8)
            if len(result) == 0:
                result = sqs.filter(content='United States')
            self.assertEqual(2, len(result))
            self.assertEqual('cyberpresse/2012/12/01/1564248', result[0].docid)
            self.assertEqual('cyberpresse/2012/12/01/1564741', result[1].docid)
            self.assertIn(escape(reference.text), result[1].text)

        with translation.override('de'):
            # test the search queryset
            sqs = SearchQuerySet()
            result = sqs.filter(content='Früherkennungstest')
            self.assertEqual(1, len(result))
            self.assertEqual('cyberpresse/2012/12/01/1564741', result[0].docid)
            self.assertIn(escape(reference.text), result[0].text)
