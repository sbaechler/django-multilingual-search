# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.core.urlresolvers import reverse
from django.views.generic import ListView, RedirectView
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


class LanguageRedirectView(RedirectView):
    def get_redirect_url(self):
        return reverse('home')
