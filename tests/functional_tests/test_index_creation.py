# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.test import TestCase
from django.utils import translation
import time
from django.utils.html import escape
from testproject.models import Document
from unittests.mocks import Data
from multilingual.elasticsearch import ElasticsearchMultilingualSearchBackend, \
    ElasticsearchMultilingualSearchEngine


class IndexTest(TestCase):
    """
    Tests the index creation functions against a real Elasitcsearch server.
    """
    fixtures = ['documents']
    index_exists = False

    def setUp(self):
        self.count = 52

    def tearDown(self):
        if self.index_exists:
            engine = ElasticsearchMultilingualSearchEngine()
            es = engine.backend('default', **Data.connection_options)
            es.clear(commit=True)
            time.sleep(1)

    def test_fixture_and_elasticsearch_up(self):
        documents = Document.objects.all()
        self.assertEqual(len(documents), self.count)
        languages = [l[0] for l in settings.LANGUAGES]
        es = ElasticsearchMultilingualSearchBackend('default', **Data.connection_options)
        self.assertEqual(languages, es.languages)

        self.assertTrue(es.conn.ping())
        info = es.conn.info()
        self.assertEqual('elasticsearch', info['cluster_name'])
        self.assertEqual(200, info['status'])

    def test_multilingual_update(self):
        """
        Test the update method on the multilingual backend.
        """
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        # the indexes don't exist yet.
        for language in es.languages:
            index_name = es._index_name_for_language(language)
            self.assertFalse(es.conn.indices.exists(index_name))

        es.setup()
        self.index_exists = True
        unified_index = engine.get_unified_index()
        index = unified_index.get_index(Document)
        iterable = Document.objects.all()
        es.update(index, iterable)
        time.sleep(1)
        id = 'testproject.document.10'
        i = 0
        # use this document as a reference.
        reference = Document.objects.get(id=10)

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
