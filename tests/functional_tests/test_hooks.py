# coding: utf-8
from __future__ import absolute_import, unicode_literals, print_function
from django.test import TestCase
from django.utils import translation
from django.utils.html import escape
from django.db.models import signals
import haystack
import time
from multilingual.elasticsearch_backend import ElasticsearchMultilingualSearchEngine
from testproject.models import Document
from testproject.signals import DocumentOnlySignalProcessor
from unittests.mocks import create_documents, Data

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2


class HookTest(TestCase):

    def setUp(self):
        # Haystack stores the connection in a global variable. This has to be reset
        # because otherwise the mock is still refrenced (Django < 1.8).
        haystack.connections.reload('default')

        self.sp = DocumentOnlySignalProcessor(haystack.connections,
                                              haystack.connection_router)

    def tearDown(self):
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.clear(models=None, commit=True)
        self.sp.teardown()
        time.sleep(1)

    def test_hook_called(self):
        documents = create_documents()
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.clear(models=None, commit=True)
        self.assertTrue(signals.post_save.has_listeners(sender=Document))

        unified_index = engine.get_unified_index()
        index = unified_index.get_index(Document)
        iterable = Document.objects.all()
        es.update(index, iterable)
        time.sleep(1)

        self.assertTrue(es.conn.indices.exists('testproject-en'))
        count = es.conn.count(index='testproject-en')
        self.assertEqual(0, count['count'])

        # write a new entry in the database
        documents[0].save()
        reference = documents[0].object
        self.assertIsNotNone(reference.id)
        id = 'testproject.document.1'
        time.sleep(0.5)

        self.assertFalse(isinstance(es.conn, mock.Mock))

        for language in es.languages:
            index_name = es._index_name_for_language(language)
            self.assertTrue(es.conn.indices.exists(index_name))
            count = es.conn.count(index=index_name)
            print(count)

            self.assertEqual(1, count['count'], 'Index %s contains the document' % index_name)
            self.assertTrue(es.conn.exists(index=index_name, doc_type='_all', id=id))
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
