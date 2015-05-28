# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import SimpleTestCase, TestCase
from django.conf import settings
from django.utils import translation
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, \
    ElasticsearchSearchEngine
from haystack.management.commands.update_index import do_update
from haystack.query import SearchQuerySet
from multilingual.elasticsearch_backend import ElasticsearchMultilingualSearchBackend, \
    ElasticsearchMultilingualSearchEngine
from .mocks import mock_indices, Data
from testproject.models import Document
from multilingual.utils import get_analyzer_for

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2


@mock.patch('elasticsearch.Elasticsearch')
class BackendTest(SimpleTestCase):
    maxDiff = None
    searchqueryset = SearchQuerySet()

