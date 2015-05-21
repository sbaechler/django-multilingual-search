from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from haystack.views import search_view_factory
from .views import DocumentView, Search, LanguageRedirectView

search_view = search_view_factory(Search)

urlpatterns = patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/', search_view, name='search'),
    (r'^$', LanguageRedirectView.as_view()),
    (r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns(
    url(r'^$', DocumentView.as_view(), name='home'),
)
