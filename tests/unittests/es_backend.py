# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import SimpleTestCase
from multilingual.elasticsearch_backend import ElasticsearchMultilingualSearchBackend
from .mocks import mock_indices, Data

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2





@mock.patch('elasticsearch.Elasticsearch')
class MockingTest(SimpleTestCase):

    def test_mocking_works(self, mock_obj):
        # create a backend instance
        es = ElasticsearchMultilingualSearchBackend('default', **Data.connection_options)
        # in the constructor, an Elasticsearche instance is created as 'conn' property.
        self.assertTrue(isinstance(es.conn, mock.Mock))
        self.assertIsNot(es.conn, mock_obj)  # a new mock is created.
        indices = mock_indices()  # use the indices mock from the mocks module.
        es.conn.attach_mock(indices, 'indices')
        self.assertEqual(es.conn.indices.get_mapping(), Data.existing_mapping)
        es.setup()
        # Data.connection_options.INDEX_NAME
        indices.get_mapping.assert_called_with(index='testproject')
