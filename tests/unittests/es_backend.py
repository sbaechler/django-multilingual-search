# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.test import TestCase


class Data:
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


class ESBackendTest(TestCase):
    pass