# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.conf import settings as django_settings
from django.utils import translation
import elasticsearch
from elasticsearch import NotFoundError, ImproperlyConfigured
import haystack
from haystack.backends import BaseEngine
from haystack.backends.elasticsearch_backend import (
    ElasticsearchSearchBackend, ElasticsearchSearchQuery, FIELD_MAPPINGS, DEFAULT_FIELD_MAPPING)
from haystack.constants import DJANGO_CT, DJANGO_ID
from haystack.utils import get_identifier
from .utils import get_analyzer_for


class ElasticsearchMultilingualSearchBackend(ElasticsearchSearchBackend):
    """
    Subclasses the Haystack backend.
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
        self._reset_existing_mapping()
        self.content_field_name = ''

    def _index_name_for_language(self, language):
        return '{0}-{1}'.format(self.index_base_name, language)

    def _reset_existing_mapping(self):
        self.existing_mapping = dict((l, {}) for l, v in django_settings.LANGUAGES)

    def setup(self):
        """
        Defers loading until needed.
        Compares the existing mapping for each language with the current codebase.
        If they differ, it automatically updates the index.
        """
        # Get the existing mapping & cache it. We'll compare it
        # during the ``update`` & if it doesn't match, we'll put the new
        # mapping.
        for language in self.languages:
            self.index_name = self._index_name_for_language(language)
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
                    self.conn.indices.create(
                        index=self.index_name,
                        body=self.DEFAULT_SETTINGS,
                        ignore=400)
                    self.conn.indices.put_mapping(
                        index=self.index_name,
                        doc_type='modelresult',
                        body=current_mapping
                    )
                    self.existing_mapping[language] = current_mapping
                except Exception:
                    if not self.silently_fail:
                        raise

        self.setup_complete = True

    def clear(self, models=[], commit=True):
        """
        Clears all indexes for the current project.
        :param models: if specified, only deletes the entries for the given models.
        :param commit: This is ignored by Haystack (maybe a bug?)
        """
        for language in self.languages:
            self.log.debug('clearing index for {0}'.format(language))
            self.index_name = self._index_name_for_language(language)
            super(ElasticsearchMultilingualSearchBackend, self).clear(models, commit)
        self._reset_existing_mapping()

    def update(self, index, iterable, commit=True):
        """
        Updates the index with current data.
        :param index: The search_indexes.Index object
        :param iterable: The queryset
        :param commit: commit to the backend.
        """
        # setup here because self.existing_mappings are overridden.
        if not self.setup_complete:
            try:
                self.setup()
            except elasticsearch.TransportError as e:
                if not self.silently_fail:
                    raise

                self.log.error("Failed to add documents to Elasticsearch: %s", e)
                return

        for language in self.languages:
            self.index_name = self._index_name_for_language(language)
            self.log.debug('updating index for {0}'.format(language))
            with translation.override(language):
                super(ElasticsearchMultilingualSearchBackend, self).update(index, iterable, commit)

    def build_schema(self, fields, language):
        """
        Build the index schema for the given field. New argument language.
        :param fields:
        :param language: the language code
        :return: a dictionary wit the field name (string) and the
                 mapping configuration (dictionary)
        """
        content_field_name = ''
        mapping = {
            DJANGO_CT: {'type': 'string', 'index': 'not_analyzed', 'include_in_all': False},
            DJANGO_ID: {'type': 'string', 'index': 'not_analyzed', 'include_in_all': False},
        }

        for field_name, field_class in fields.items():
            field_mapping = FIELD_MAPPINGS.get(
                field_class.field_type, DEFAULT_FIELD_MAPPING).copy()
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

    def search(self, query_string, **kwargs):
        """
        The main search method
        :param query_string: The string to pass to Elasticsearch. e.g. '*:*'
        :param kwargs: start_offset, end_offset, result_class
        :return: result_class instance
        """
        self.index_name = self._index_name_for_language(translation.get_language())
        self.log.debug('search method called (%s): %s' %
                       (translation.get_language(), query_string))
        return super(ElasticsearchMultilingualSearchBackend, self).search(query_string, **kwargs)

    def remove(self, obj_or_string, commit=True):
        """
        Removes an object from the index.
        :param obj_or_string:
        :param commit:
        """
        if not self.setup_complete:
            try:
                self.setup()
            except elasticsearch.TransportError as e:
                if not self.silently_fail:
                    raise
                doc_id = get_identifier(obj_or_string)
                self.log.error("Failed to remove document '%s' from Elasticsearch: %s", doc_id, e)
                return

        for language in self.languages:
            self.log.debug('removing {0} from index {1}'.format(obj_or_string, language))
            self.index_name = self._index_name_for_language(language)
            with translation.override(language):
                super(ElasticsearchMultilingualSearchBackend, self).remove(obj_or_string,
                                                                           commit=commit)


class ElasticsearchMultilingualSearchQuery(ElasticsearchSearchQuery):
    """ The original class is good enough for now. """


class ElasticsearchMultilingualSearchEngine(BaseEngine):
    backend = ElasticsearchMultilingualSearchBackend
    query = ElasticsearchMultilingualSearchQuery
