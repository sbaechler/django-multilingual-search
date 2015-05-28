# coding: utf-8
from __future__ import absolute_import, unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from .models import Document


class DocumentTranslationOptions(TranslationOptions):
    fields = ('title', 'text')

translator.register(Document, DocumentTranslationOptions)
