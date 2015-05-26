# coding: utf-8
from __future__ import absolute_import, unicode_literals
from elasticsearch import NotFoundError, ImproperlyConfigured
from haystack.backends import BaseEngine
import haystack
from django.conf import settings as django_settings

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

        if not hasattr(django_settings, 'LANGUAGES'):
            raise ImproperlyConfigured("You must specify 'LANGUAGES' in your Django settings.")
        self.languages = [l[0] for l in django_settings.LANGUAGES]
        self.existing_mapping = {l: {} for (l, v) in django_settings.LANGUAGES}

    def setup(self):
        """
        Defers loading until needed.
        """
        # Get the existing mapping & cache it. We'll compare it
        # during the ``update`` & if it doesn't match, we'll put the new
        # mapping.
        for language in self.languages:
            try:
                self.existing_mapping[language] = self.conn.indices.get_mapping(
                    index='{0}-{1}'.format(self.index_name, language))
            except NotFoundError:
                pass
            except Exception:
                if not self.silently_fail:
                    raise

        unified_index = haystack.connections[self.connection_alias].get_unified_index()
        self.content_field_name, field_mapping = self.build_schema(unified_index.all_searchfields())
        current_mapping = {
            'modelresult': {
                'properties': field_mapping,
                '_boost': {
                    'name': 'boost',
                    'null_value': 1.0
                }
            }
        }

        for language in self.languages:
            if current_mapping != self.existing_mapping[language]:
                index_name = '{0}-{1}'.format(self.index_name, language)
                try:
                    # Make sure the index is there first.
                    self.conn.indices.create(index=index_name,
                                             body=self.DEFAULT_SETTINGS, ignore=400)
                    self.conn.indices.put_mapping(index=index_name,
                                                  doc_type='modelresult', body=current_mapping)
                    self.existing_mapping[language] = current_mapping
                except Exception:
                    if not self.silently_fail:
                        raise

        self.setup_complete = True

    def clear(self, models=[], commit=True):
        raise NotImplementedError('TODO: clear method')



class ElasticsearchMultilingualSearchEngine(BaseEngine):
    backend = ElasticsearchMultilingualSearchBackend
    query = ElasticsearchSearchQuery
