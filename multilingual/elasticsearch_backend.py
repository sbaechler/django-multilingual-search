# coding: utf-8
from __future__ import absolute_import, unicode_literals
from haystack.backends import BaseEngine

from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, \
    ElasticsearchSearchQuery


class ElasticsearchMultilingualSearchBackend(ElasticsearchSearchBackend):
    """
    Subclasses the original backend.
    """
    def __init__(self, connection_alias, **connection_options):
        """
        :param connection_alias: The connection name. Usually 'default'
        :param connection_options: The connection settings.
        """
        super(ElasticsearchMultilingualSearchBackend, self).__init__(
            connection_alias, **connection_options)


class ElasticsearchMultilingualSearchEngine(BaseEngine):
    backend = ElasticsearchMultilingualSearchBackend
    query = ElasticsearchSearchQuery
