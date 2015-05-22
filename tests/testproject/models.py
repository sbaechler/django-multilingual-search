# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db import models


class Document(models.Model):
    docid = models.CharField(max_length=100)
    genre = models.CharField(max_length=20)
    origlang = models.CharField(max_length=10)
    text = models.TextField()
    title = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Document'
        ordering = ['docid']

    def __unicode__(self):
        return '{0} ({1})'.format(self.title, self.docid)

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.docid)
