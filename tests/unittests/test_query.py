# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import SimpleTestCase
from django.utils import translation

from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
from haystack.query import SearchQuerySet
from multilingual.elasticsearch_backend import ElasticsearchMultilingualSearchQuery, \
    ElasticsearchMultilingualSearchBackend
from .mocks import Data, mock_backend

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2


class BackendTest(SimpleTestCase):
    maxDiff = None

    # django_ct list has a random order.
    def assert_called_with_search_kwargs(self, search):
        try:
            search.assert_called_with(**Data.search_kwargs)
        except AssertionError:
            Data.search_kwargs['body']['query']['filtered']['filter']['terms']['django_ct'].reverse()  # noqa
            search.assert_called_with(**Data.search_kwargs)

    @mock.patch('elasticsearch.Elasticsearch')
    def test_query(self, mock_es):
        sqs = SearchQuerySet()
        self.assertFalse(sqs.query.has_run())
        self.assertIsInstance(sqs.query, ElasticsearchMultilingualSearchQuery)
        all_results = sqs.all()
        all_results.query.backend = mock_backend()
        list(all_results)
        self.assertTrue(all_results.query.backend.search.called)
        self.assertEqual('*:*', all_results.query.backend.search.call_args[0][0])

    @mock.patch('elasticsearch.Elasticsearch')
    def test_haystack_search(self, mock_es):
        es = ElasticsearchSearchBackend('default', **Data.connection_options)
        self.assertFalse(es.setup_complete)
        es.setup()
        es.search('*:*', end_offset=1)
        # es.conn.search.assert_called_with(**Data.search_kwargs)
        self.assert_called_with_search_kwargs(es.conn.search)

    @mock.patch('elasticsearch.Elasticsearch')
    def test_multilingual_search(self, mock_es):
        es = ElasticsearchMultilingualSearchBackend('default', **Data.connection_options)
        es.setup()
        kwargs = Data.search_kwargs.copy()
        for language in ['de', 'en', 'ru']:
            with translation.override(language):
                es.search('*:*', end_offset=1)
                kwargs['index'] = es._index_name_for_language(language)
                es.conn.search.assert_called_with(**kwargs)

    @mock.patch('elasticsearch.Elasticsearch')
    def test_haystack_process_results(self, mock_es):
        es = ElasticsearchSearchBackend('default', **Data.connection_options)
        es.setup()
        results = es._process_results(Data.raw_results)
        expected = {'hits': 0, 'spelling_suggestion': None, 'results': [], 'facets': {}}
        self.assertEqual(expected, results)

    @mock.patch('elasticsearch.Elasticsearch')
    def test_multiligual_process_results(self, mock_es):
        es = ElasticsearchMultilingualSearchBackend('default', **Data.connection_options)
        es.setup()
        results = es._process_results(Data.raw_results)
        expected = {'hits': 0, 'spelling_suggestion': None, 'results': [], 'facets': {}}
        self.assertEqual(expected, results)
