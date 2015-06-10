# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db import models
from haystack import signals
from .models import Document

class DocumentOnlySignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        # Listen only to the ``Document`` model.
        models.signals.post_save.connect(self.handle_save, sender=Document)
        models.signals.post_delete.connect(self.handle_delete, sender=Document)

    def teardown(self):
        # Disconnect only for the ``Document`` model.
        models.signals.post_save.disconnect(self.handle_save, sender=Document)
        models.signals.post_delete.disconnect(self.handle_delete, sender=Document)
