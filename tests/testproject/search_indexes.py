# coding: utf-8
from __future__ import absolute_import, unicode_literals

from haystack import indexes
from .models import Document

class DocumentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    docid = indexes.CharField(model_attr='docid')

    def get_model(self):
        return Document
