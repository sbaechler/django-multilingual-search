# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils import translation
from elasticsearch import NotFoundError, ImproperlyConfigured
import elasticsearch
from haystack.backends import BaseEngine
import haystack
from django.conf import settings as django_settings

from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, \
    ElasticsearchSearchQuery, FIELD_MAPPINGS, DEFAULT_FIELD_MAPPING
from haystack.constants import DJANGO_CT, DJANGO_ID
from .utils import get_analyzer_for


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

        # self.index_name will be modified for each translation.
        self.index_base_name = self.index_name
        if not hasattr(django_settings, 'LANGUAGES'):
            raise ImproperlyConfigured("You must specify 'LANGUAGES' in your Django settings.")
        self.languages = [l[0] for l in django_settings.LANGUAGES]
        self.existing_mapping = {l: {} for (l, v) in django_settings.LANGUAGES}
        self.content_field_name = ''

    def index_name_for_language(self, language):
        return '{0}-{1}'.format(self.index_base_name, language)

    def setup(self):
        """
        Defers loading until needed.
        """
        # Get the existing mapping & cache it. We'll compare it
        # during the ``update`` & if it doesn't match, we'll put the new
        # mapping.
        for language in self.languages:
            self.index_name = self.index_name_for_language(language)
            try:
                self.existing_mapping[language] = self.conn.indices.get_mapping(
                    index=self.index_name)
            except NotFoundError:
                pass
            except Exception:
                if not self.silently_fail:
                    raise

            unified_index = haystack.connections[self.connection_alias].get_unified_index()

            self.content_field_name, field_mapping = self.build_schema(
                unified_index.all_searchfields(), language)

            current_mapping = {
                'modelresult': {
                    'properties': field_mapping,
                    '_boost': {
                        'name': 'boost',
                        'null_value': 1.0
                    }
                }
            }

            if current_mapping != self.existing_mapping[language]:
                try:
                    # Make sure the index is there first.
                    self.conn.indices.create(index=self.index_name,
                                             body=self.DEFAULT_SETTINGS, ignore=400)
                    self.conn.indices.put_mapping(index=self.index_name,
                                                  doc_type='modelresult', body=current_mapping)
                    self.existing_mapping[language] = current_mapping
                except Exception:
                    if not self.silently_fail:
                        raise

        self.setup_complete = True

    def clear(self, models=[], commit=True):
        for language in self.languages:
            self.index_name = self.index_name_for_language(language)
            super(ElasticsearchMultilingualSearchBackend, self).clear(models, commit)
        self.existing_mapping = {l: {} for (l, v) in django_settings.LANGUAGES}

    def update(self, index, iterable, commit=True):
        """
        Updates the index with current data.
        :param index: The search_indexes.Index object
        :param iterable: The queryset
        :param commit: commit to the backend.
        """
        if not self.setup_complete:
            try:
                self.setup()
            except elasticsearch.TransportError as e:
                if not self.silently_fail:
                    raise

                self.log.error("Failed to add documents to Elasticsearch: %s", e)
                return

        for language in self.languages:
            self.index_name = self.index_name_for_language(language)
            with translation.override(language):
                super(ElasticsearchMultilingualSearchBackend, self).update(index, iterable, commit)

    def build_schema(self, fields, language):
        content_field_name = ''
        mapping = {
            DJANGO_CT: {'type': 'string', 'index': 'not_analyzed', 'include_in_all': False},
            DJANGO_ID: {'type': 'string', 'index': 'not_analyzed', 'include_in_all': False},
        }

        for field_name, field_class in fields.items():
            field_mapping = FIELD_MAPPINGS.get(field_class.field_type, DEFAULT_FIELD_MAPPING).copy()
            if field_class.boost != 1.0:
                field_mapping['boost'] = field_class.boost

            if field_class.document is True:
                content_field_name = field_class.index_fieldname

            # Do this last to override `text` fields.
            if field_mapping['type'] == 'string':
                # Use the language analyzer for text fields.
                if field_mapping['analyzer'] == DEFAULT_FIELD_MAPPING['analyzer']:
                    field_mapping['analyzer'] = get_analyzer_for(language)
                if field_class.indexed is False or hasattr(field_class, 'facet_for'):
                    field_mapping['index'] = 'not_analyzed'
                    del field_mapping['analyzer']

            mapping[field_class.index_fieldname] = field_mapping

        return content_field_name, mapping


class ElasticsearchMultilingualSeqrchQuery(ElasticsearchSearchQuery):
    def run(self, spelling_query=None, **kwargs):
        super(ElasticsearchMultilingualSeqrchQuery, self).run(spelling_query, **kwargs)


class ElasticsearchMultilingualSearchEngine(BaseEngine):
    backend = ElasticsearchMultilingualSearchBackend
    query = ElasticsearchMultilingualSeqrchQuery
