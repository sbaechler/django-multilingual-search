# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import TestCase
from django.utils import translation
from django.utils.html import escape
import haystack
from haystack.signals import RealtimeSignalProcessor
from multilingual.elasticsearch import ElasticsearchMultilingualSearchBackend, \
    ElasticsearchMultilingualSearchEngine
from testproject.models import Document
from unittests.mocks import create_documents, Data


class HookTest(TestCase):

    def test_hook_called(self):
        documents = create_documents()
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.clear(commit=True)

        es.setup()
        unified_index = engine.get_unified_index()
        index = unified_index.get_index(Document)
        iterable = Document.objects.all()
        es.update(index, iterable)

        signal_processor = RealtimeSignalProcessor(haystack.connections,
                                           haystack.connection_router)
        self.assertTrue(es.conn.indices.exists('testproject-en'))
        count = es.conn.count(index='testproject-en')
        self.assertEqual(0, count['count'])

        # write a new entry in the database
        documents[0].save()
        reference = documents[0].object
        id = 'testproject.document.1'

        for language in es.languages:
            index_name = es.index_name_for_language(language)
            self.assertTrue(es.conn.indices.exists(index_name))
            count = es.conn.count(index=index_name)
            self.assertEqual(1, count['count'])

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
            index_name = es.index_name_for_language(language)
            self.assertTrue(es.conn.indices.exists(index_name))
            count = es.conn.count(index=index_name)
            self.assertEqual(0, count['count'])
