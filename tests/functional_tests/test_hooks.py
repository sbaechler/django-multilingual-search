# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import TestCase
from django.utils import translation
from django.utils.html import escape
import haystack
from haystack.signals import RealtimeSignalProcessor
import time
from multilingual.elasticsearch import ElasticsearchMultilingualSearchEngine
from testproject.models import Document
from unittests.mocks import create_documents, Data

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2


class HookTest(TestCase):

    def tearDown(self):
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.clear(commit=True)
        time.sleep(1)

    def test_hook_called(self):
        documents = create_documents()
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.clear(commit=True)

        unified_index = engine.get_unified_index()
        index = unified_index.get_index(Document)
        iterable = Document.objects.all()
        es.update(index, iterable)
        time.sleep(1)
        rsp = RealtimeSignalProcessor(haystack.connections, haystack.connection_router)  # noqa
        self.assertFalse(isinstance(rsp.handle_save, mock.Mock))
        self.assertTrue(es.conn.indices.exists('testproject-en'))
        count = es.conn.count(index='testproject-en')
        self.assertEqual(0, count['count'])

        # write a new entry in the database
        documents[0].save()
        reference = documents[0].object
        id = 'testproject.document.1'
        time.sleep(0.5)
        for language in es.languages:
            index_name = es._index_name_for_language(language)
            self.assertTrue(es.conn.indices.exists(index_name))
            count = es.conn.count(index=index_name)
            self.assertEqual(1, count['count'], 'Index %s contains the document' % index_name)

            self.assertTrue(es.conn.exists(index=index_name, id=id))
            doc = es.conn.get(index=index_name, id=id)
            self.assertTrue(doc['found'])
            self.assertEqual(doc['_type'], 'modelresult')
            self.assertEqual(doc['_source']['docid'], reference.docid)
            with translation.override(language):
                self.assertIn(escape(reference.text), doc['_source']['text'])

        # delete the object. The object needs to be removed from the index.
        reference.delete()
        for language in es.languages:
            index_name = es._index_name_for_language(language)
            self.assertTrue(es.conn.indices.exists(index_name))
            count = es.conn.count(index=index_name)
            self.assertEqual(0, count['count'])
