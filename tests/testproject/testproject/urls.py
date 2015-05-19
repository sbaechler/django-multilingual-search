from django.conf.urls import include, url
from django.contrib import admin
from haystack.views import search_view_factory
from .views import DocumentView, LanguageView, Search

search_view = search_view_factory(Search)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/', search_view, name='search'),
    url(r'^$', DocumentView.as_view(), name='home'),
    url(r'^(en|de|es|fr|cs|ru)/$', LanguageView.as_view(), name='language_home'),
]
