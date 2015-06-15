# django-multilingual-search
A multilingual Haystack plugin for Django and Elasticsearch.
The module is a drop-in replacement for the Haystack `ElasticsearchSearchEngine`.

Instead of a single index it creates an index for each language specified in `settings.LANGUAGES`.

A query is routed to the index of the currently active language.

[![Build Status](https://travis-ci.org/sbaechler/django-multilingual-search.svg?branch=master)](https://travis-ci.org/sbaechler/django-multilingual-search)

## Installation

Install with pip:

    pip install django-multilingual-search
    
The major and minor versions of this project correspond to the Haystack version the package was
tested against. This version is for Haystack 2.4.
    
    
## Configuration

The app provides a drop-in replacement for the ElasticsearchEngine of Haystack.
To use it, specify this engine in `settings.py`:

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'multilingual.elasticsearch.ElasticsearchMultilingualSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'myproject',
        },
    }
    
For automatic indexing of new entries the Haystack 
[signal processors](http://django-haystack.readthedocs.org/en/latest/signal_processors.html) 
can be used without modification. It is recommended that a custom SignalProcessor be used
instead of the `RealtimeSignalProcessor` because of server timeout issues with the latter.


## Contributing

Please read the [Contributing](./CONTRIBUTING.md) guide.


## Release History

- 2.3.0: First release
- 2.4.0: Update code for compatibility with Haystack 2.4