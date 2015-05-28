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
        'SILENTLY_FAIL': False,
    }
    existing_mapping = {'modelresult': {'_boost': {'null_value': 1.0, 'name': 'boost'},
                                        'properties': {'django_id': {'index': 'not_analyzed',
                                                                     'include_in_all': False,
                                                                     'type': 'string'},
                                                       'docid': {'analyzer': 'snowball',
                                                                 'type': 'string'},
                                                       'django_ct': {'index': 'not_analyzed',
                                                                     'include_in_all': False,
                                                                     'type': 'string'},
                                                       'text': {'analyzer': 'snowball',
                                                                'type': 'string'}}}}

    # same as modelresult.properties
    field_mapping = {'text': {'type': 'string', 'analyzer': 'snowball'},
                     'django_ct': {'type': 'string', 'index': 'not_analyzed',
                                   'include_in_all': False},
                     'docid': {'type': 'string', 'analyzer': 'snowball'},
                     'django_id': {'type': 'string', 'index': 'not_analyzed',
                                   'include_in_all': False}}

    index_keys = ['django_ct', 'id', 'text', 'docid', 'django_id', '_id']

    search_kwargs = {'_source': True, 'doc_type': 'modelresult', 'index': 'testproject',
                     'body': {'query': {'filtered': {'query': {'match_all': {}},
                              'filter': {'terms': {'django_ct': ['testproject.document']}}}},
                              'from': 0, 'size': 1}}

    raw_results = {'timed_out': False,
                   '_shards': {'failed': 0, 'total': 5, 'successful': 5},
                   'hits': {'total': 0, 'max_score': None, 'hits': []}, 'took': 7}


def mock_indices():
    mymock = mock.Mock()
    attrs = {'get_mapping.return_value': Data.existing_mapping}

    mymock.configure_mock(**attrs)
    return mymock


def mock_backend():
    mymock = mock.Mock()
    attrs = {'search.return_value': {}}
    mymock.configure_mock(**attrs)
    return mymock
