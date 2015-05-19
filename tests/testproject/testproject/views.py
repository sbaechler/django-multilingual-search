# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.views.generic import ListView
from haystack.forms import HighlightedSearchForm
from haystack.views import SearchView
from .models import Document


class SearchForm(HighlightedSearchForm):
    pass


class DocumentView(ListView):
    model = Document
    paginate_by = 20


class Search(SearchView):
    form = SearchForm
    model = Document
    paginate_by = 20


class LanguageView(ListView):

    template_name = 'testproject/document_list.html'

    def get_queryset(self):
        return Document.objects.filter(language=self.args[0])
