# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Document(models.Model):
    """ The document model class to test the library with
        django-modeltranslations.
    """
    docid = models.CharField(max_length=100)
    genre = models.CharField(max_length=20)
    origlang = models.CharField(max_length=10)
    text = models.TextField()
    title = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Modeltranslations Document'
        ordering = ['docid']

    def __unicode__(self):
        return '{0} ({1})'.format(self.title, self.docid)

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.docid)


class ParlerDocument(TranslatableModel):
    """ The document model class to test the library with
        django-parler
    """
    docid = models.CharField(max_length=100)
    genre = models.CharField(max_length=20)
    origlang = models.CharField(max_length=10)

    translations = TranslatedFields(
        text=models.TextField(),
        title=models.TextField(blank=True),
    )

    class Meta:
        verbose_name = 'Parler Document'
        ordering = ['docid']

    def __unicode__(self):
        return '{0} ({1})'.format(self.title, self.docid)

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.docid)
