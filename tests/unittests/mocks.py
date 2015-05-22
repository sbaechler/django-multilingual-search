# coding: utf-8
from __future__ import absolute_import, unicode_literals

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2


class Data:
    connection_options = {
        'ENGINE': 'multilingual.elasticsearch_backend.ElasticsearchMultilingualSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'testproject',
    }
    existing_mapping = {'testproject': {'mappings': {'modelresult': {
        'properties': {'docid': {'type': 'string', 'analyzer': 'snowball'},
                       'django_ct': {'type': 'string', 'index': 'not_analyzed',
                                     'include_in_all': False},
                       'django_id': {'type': 'string', 'index': 'not_analyzed',
                                     'include_in_all': False},
                       'text': {'type': 'string', 'analyzer': 'snowball'},
                       'id': {'type': 'string'}},
        '_boost': {'null_value': 1.0, 'name': 'boost'}}}}}

    # same as modelresult.properties
    field_mapping = {'text': {'type': 'string', 'analyzer': 'snowball'},
                     'django_ct': {'type': 'string', 'index': 'not_analyzed',
                                   'include_in_all': False},
                     'docid': {'type': 'string', 'analyzer': 'snowball'},
                     'django_id': {'type': 'string', 'index': 'not_analyzed',
                                   'include_in_all': False}}

    index_keys = ['django_ct', 'id', 'text', 'docid', 'django_id', '_id']





def mock_indices():
    mymock = mock.Mock()
    attrs = {'get_mapping.return_value': Data.existing_mapping}

    mymock.configure_mock(**attrs)
    return mymock
