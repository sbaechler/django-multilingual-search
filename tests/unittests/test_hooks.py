# coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.conf import settings
import haystack
from haystack.signals import RealtimeSignalProcessor

from testproject.models import Document
from .mocks import create_documents

try:
    from unittest import mock  # python >= 3.3
except ImportError:
    import mock  # python 2


@mock.patch('elasticsearch.Elasticsearch')
class BackendTest(TestCase):
    maxDiff = None

    def test_post_save_and_delete_hook(self, es_obj):
        # index uses a global loader for the backend.
        documents = create_documents()
        doc = documents[0]
        doc.save()
        # send the post_save signal
        index = haystack.connections['default'].get_unified_index().get_index(Document)
        index.update_object(doc.object, 'default')
        backend = index._get_backend('default')
        # test if the command has been sent to ES
        es = backend.conn
        self.assertFalse(es.delete.called)
        self.assertTrue(es.bulk.called)
        call_args = es.bulk.call_args_list
        self.assertEqual(len(call_args), len(settings.LANGUAGES))
        self.assertEqual(call_args[0][0][0][0], {'index': {'_id': 'testproject.document.1'}})
        index_list = [a[1] for a in call_args]
        self.assertIn({'doc_type': 'modelresult', 'index': 'testproject-en'}, index_list)
        self.assertIn({'doc_type': 'modelresult', 'index': 'testproject-de'}, index_list)
        self.assertIn({'doc_type': 'modelresult', 'index': 'testproject-es'}, index_list)
        self.assertIn(doc.object.text_en, call_args[0][0][0][1]['text'])
        # test delete
        index.remove_object(doc.object, 'default')

        self.assertTrue(es.delete.called)
        call_args = es.delete.call_args_list
        self.assertEqual(len(call_args), len(settings.LANGUAGES))
        self.assertEqual(call_args[0][1],
                         {'index': 'testproject-en', 'ignore': 404,
                          'doc_type': 'modelresult', 'id': 'testproject.document.1'})
        self.assertEqual(call_args[1][1],
                         {'id': 'testproject.document.1', 'doc_type': 'modelresult',
                         'ignore': 404, 'index': 'testproject-de'})

    @mock.patch.object(RealtimeSignalProcessor, 'handle_save')
    @mock.patch.object(RealtimeSignalProcessor, 'handle_delete')
    def test_hook_called(self, mock_delete, mock_save, mock_es):
        # check if the signals are triggered
        signal_processor = RealtimeSignalProcessor(haystack.connections,
                                                   haystack.connection_router)
        self.assertFalse(mock_delete.called)
        self.assertFalse(mock_save.called)
        documents = create_documents()
        doc = documents[0]
        doc.save()
        self.assertTrue(mock_save.called)
        doc.object.delete()
        self.assertTrue(mock_delete.called)
