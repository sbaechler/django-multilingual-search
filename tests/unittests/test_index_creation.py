# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import SimpleTestCase, TestCase
from django.conf import settings
from django.utils import translation
from django.utils.html import escape
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, \
    ElasticsearchSearchEngine
from haystack.management.commands.update_index import do_update
from multilingual.elasticsearch_backend import ElasticsearchMultilingualSearchBackend, \
    ElasticsearchMultilingualSearchEngine
from .mocks import mock_indices, Data
from testproject.models import Document
from multilingual.utils import get_analyzer_for

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2


class BackendTest(SimpleTestCase):
    maxDiff = None

    @mock.patch('elasticsearch.Elasticsearch')
    def test_mocking_works(self, mock_obj):
        # create a backend instance
        es = ElasticsearchMultilingualSearchBackend('default', **Data.connection_options)
        for language in settings.LANGUAGES:
            self.assertIn(language[0], es.existing_mapping.keys())
        # in the constructor, an Elasticsearche instance is created as 'conn' property.
        self.assertTrue(isinstance(es.conn, mock.Mock))
        self.assertIsNot(es.conn, mock_obj)  # a new mock is created.
        self.assertFalse(es.silently_fail)
        indices = mock_indices()  # use the indices mock from the mocks module.
        es.conn.attach_mock(indices, 'indices')
        self.assertEqual(es.conn.indices.get_mapping(), Data.existing_mapping)
        es.setup()
        # Data.connection_options.INDEX_NAME
        indices.get_mapping.assert_any_call(index='testproject-en')
        indices.get_mapping.assert_any_call(index='testproject-de')
        indices.get_mapping.assert_any_call(index='testproject-ru')

    @mock.patch('elasticsearch.Elasticsearch')
    def test_do_update(self, mock_obj):
        """
        Tests the update_index.do_update function
        """
        engine = ElasticsearchMultilingualSearchEngine()
        backend = mock.Mock()
        engine._backend = backend
        index = engine.get_unified_index()
        qs = Document.objects.all()
        start = 0
        end = len(qs)
        total = end - start
        do_update(backend, index, qs, start, end, total, verbosity=1)
        # The update method has been called
        self.assertTrue(backend.update.called)
        call_args_list = backend.update.call_args_list
        # args, the queryset cannot be testet for equality.
        self.assertEqual(call_args_list[0][0][0], index)
        # kwargs
        # self.assertEqual(call_args_list[0][1], {'commit': False})  only Haystack >= 2.4

    @mock.patch('elasticsearch.Elasticsearch')
    def test_setup_on_haystack_backend(self, mock_obj):
        """
        Tests the Setup method on the elasticsearch backend.
        """
        es = ElasticsearchSearchBackend('default', **Data.connection_options)
        self.assertFalse(es.setup_complete)
        es.setup()
        self.assertTrue(es.setup_complete)
        self.assertEqual(es.existing_mapping, Data.existing_mapping)
        es.conn.indices.create.assert_called_with(index='testproject',
                                                  ignore=400, body=es.DEFAULT_SETTINGS)
        es.conn.indices.put_mapping.assert_called_with(index='testproject',
                                                       doc_type='modelresult',
                                                       body=Data.existing_mapping)

    @mock.patch('elasticsearch.Elasticsearch')
    def test_setup_on_multilingual_backend(self, mock_obj):
        """
        Tests the Setup method on the elasticsearch backend.
        """
        es = ElasticsearchMultilingualSearchBackend('default', **Data.connection_options)
        self.assertFalse(es.setup_complete)
        es.setup()
        self.assertTrue(es.setup_complete)
        self.assertNotEqual(es.existing_mapping['de'], Data.existing_mapping)
        self.assertEqual(es.existing_mapping['de']['modelresult']['properties']['text']['analyzer'],
                         get_analyzer_for('de'))
        es.conn.indices.create.assert_any_call(index='testproject-de',
                                               ignore=400, body=es.DEFAULT_SETTINGS)
        es.conn.indices.put_mapping.assert_any_call(index='testproject-de',
                                                    doc_type='modelresult',
                                                    body=es.existing_mapping['de'])

        self.assertNotEqual(es.existing_mapping['en'], Data.existing_mapping)
        self.assertEqual(es.existing_mapping['en']['modelresult']['properties']['text']['analyzer'],
                         get_analyzer_for('en'))
        es.conn.indices.create.assert_any_call(index='testproject-en',
                                               ignore=400, body=es.DEFAULT_SETTINGS)
        es.conn.indices.put_mapping.assert_any_call(index='testproject-en',
                                                    doc_type='modelresult',
                                                    body=es.existing_mapping['en'])

        self.assertNotEqual(es.existing_mapping['fr'], Data.existing_mapping)
        self.assertEqual(es.existing_mapping['fr']['modelresult']['properties']['text']['analyzer'],
                         get_analyzer_for('fr'))
        es.conn.indices.create.assert_any_call(index='testproject-fr',
                                               ignore=400, body=es.DEFAULT_SETTINGS)
        es.conn.indices.put_mapping.assert_any_call(index='testproject-fr',
                                                    doc_type='modelresult',
                                                    body=es.existing_mapping['fr'])

    @mock.patch('elasticsearch.Elasticsearch')
    def test_haystack_clear(self, mock_obj):
        es = ElasticsearchSearchBackend('default', **Data.connection_options)
        es.setup()
        es.clear(commit=True)  # commit is ignored anyway
        es.conn.indices.delete.assert_called_with(index='testproject', ignore=404)

    @mock.patch('elasticsearch.Elasticsearch')
    def test_multilingual_clear(self, mock_obj):
        es = ElasticsearchMultilingualSearchBackend('default', **Data.connection_options)
        es.setup()
        es.clear(commit=False)
        es.conn.indices.delete.assert_any_call(index='testproject-en', ignore=404)
        es.conn.indices.delete.assert_any_call(index='testproject-fr', ignore=404)
        es.conn.indices.delete.assert_any_call(index='testproject-de', ignore=404)
        es.conn.indices.delete.assert_any_call(index='testproject-ru', ignore=404)


class IndexTest(TestCase):
    fixtures = ['small']
    maxDiff = None

    def test_fixture(self):
        qs = Document.objects.all()
        self.assertEqual(3, len(qs))

    @mock.patch('elasticsearch.Elasticsearch')
    def test_haystack_update(self, mock_obj):
        """
        Test the update method on the Haystack backend
        """
        engine = ElasticsearchSearchEngine()
        es = ElasticsearchSearchBackend('default', **Data.connection_options)
        engine._backend = es
        es.setup()
        unified_index = engine.get_unified_index()
        index = unified_index.get_index(Document)
        iterable = Document.objects.all()
        es.update(index, iterable)
        es.conn.indices.refresh.assert_called_with(index='testproject')
        self.assertTrue(es.conn.bulk.called)
        call_args = es.conn.bulk.call_args[0][0]
        self.assertEqual(6, len(call_args))
        self.assertEqual({'index': {'_id': 'testproject.document.1'}}, call_args[0])
        self.assertEqual({'index': {'_id': 'testproject.document.2'}}, call_args[2])
        self.assertEqual({'index': {'_id': 'testproject.document.3'}}, call_args[4])
        self.assertIn('Republican leaders justified their policy', call_args[1]['text'])
        doc1 = Document.objects.get(pk=1)
        self.assertIn(doc1.text, call_args[1]['text'])
        self.assertIn('the PSA test sometimes shows erroneous results', call_args[3]['text'])
        self.assertIn('The announcement of the probable discovery of the Higgs boson',
                      call_args[5]['text'])

    @mock.patch('elasticsearch.Elasticsearch')
    def test_multilingual_update(self, mock_obj):
        """
        Test the update method on the multilingual backend.
        """
        engine = ElasticsearchMultilingualSearchEngine()
        es = engine.backend('default', **Data.connection_options)
        es.setup()
        unified_index = engine.get_unified_index()
        index = unified_index.get_index(Document)
        iterable = Document.objects.all()
        es.update(index, iterable)
        es.conn.indices.refresh.assert_any_call(index='testproject-en')
        es.conn.indices.refresh.assert_any_call(index='testproject-de')
        es.conn.indices.refresh.assert_any_call(index='testproject-fr')
        self.assertTrue(es.conn.bulk.called)
        self.assertEqual(len(es.conn.bulk.call_args_list), len(settings.LANGUAGES))
        for call_args in es.conn.bulk.call_args_list:
            language = call_args[1]['index'][-2:]
            content = call_args[0][0][1]
            document = Document.objects.get(id=content['django_id'])
            self.assertEqual(document.docid, content['docid'])
            with translation.override(language):
                self.assertIn(escape(document.text), content['text'])
