# coding: utf-8
from __future__ import absolute_import, unicode_literals
from haystack.backends import BaseEngine

from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, \
    ElasticsearchSearchQuery


class ElasticsearchMultilingualSearchBackend(ElasticsearchSearchBackend):

    def __init__(self, connection_alias, **connection_options):
        super(ElasticsearchMultilingualSearchBackend, self).__init__(
            connection_alias, **connection_options)


class ElasticsearchMultilingualSearchEngine(BaseEngine):
    backend = ElasticsearchMultilingualSearchBackend
    query = ElasticsearchSearchQuery
