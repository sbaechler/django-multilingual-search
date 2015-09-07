# coding: utf-8
from __future__ import absolute_import, unicode_literals
import codecs
from django.core.management import BaseCommand
from django.utils import translation
import os
from glob import glob
from ...models import ParlerDocument, Document

try:
    from HTMLParser import HTMLParser  # Python 2
except ImportError:
    from html.parser import HTMLParser  # Python 3


class SGMLParser(HTMLParser):
    """ Parses the SGML file and create database entries.  """

    def __init__(self, model, language):
        """
        Creates the objects from the given model.
        :param model: A Django model class.
        """
        super(SGMLParser, self).__init__()
        self.model_class = model
        self.model = None
        self.text = ''
        self.is_title = False
        self.language = language

    def parse(self, data):
        self._lines = []
        self.reset()
        self.feed(data)

    # called on an opening tag
    def handle_starttag(self, tag, attrs):
        if tag == 'doc':
            self.start_new_model(attrs)
        elif tag == 'h1':
            self.is_title = True

    # called on a closing tag
    def handle_endtag(self, tag):
        if tag == 'doc':
            self.end_new_model()
        elif tag == 'h1':
            self.is_title = False
        elif tag == 'p':
            self.text += '\n'

    def handle_data(self, data):
        if data != '\n':
            if self.is_title:
                self.model.title = data
            else:
                self.text += (data + '\n')

    # create a new object instance
    def start_new_model(self, attrs):
        attributes = dict(attrs)
        self.model, created = self.model_class.objects.get_or_create(docid=attributes['docid'])
        for attr, value in attrs:
            if hasattr(self.model, attr):
                setattr(self.model, attr, value)

    # save the object instance
    def end_new_model(self):
        self.model.text = self.text
        self.text = ''
        self.model.save()
        self.model = None


class Command(BaseCommand):
    help = 'Import test data from a SGML source. The filename must end in -ref.<LANGUAGE_CODE>.sgm'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            default=False,
                            help='Delete all models before import.')

    def handle(self, *args, **options):
        if options['delete']:
            Document.objects.all().delete()

        path = options['path']
        if not os.path.isdir(path):
            raise AttributeError('Path "{0}" is not a directory'.format(path))
        files = glob(os.path.join(path, '*ref.*.sgm'))
        for file in files:
            language = file.split('.')[-2]
            translation.activate(language)
            self.stdout.write('{0}: {1}'.format(file, language))
            with codecs.open(file, 'r', 'utf-8') as f:
                modeltranslation_parser = SGMLParser(Document, language)
                parler_parser = SGMLParser(ParlerDocument, language)
                data = f.read()
            modeltranslation_parser.parse(data)
            parler_parser.parse(data)

        self.stdout.write('Done.')
