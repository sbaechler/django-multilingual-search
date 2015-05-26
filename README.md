# django-multilingual-search
A multilingual search plugin for Django and Elasticsearch

## Installation

Install with pip:

    pip install django-multilingual-search
    
    
## Configuration::

The app provides a drop-in replacement for the ElasticsearchEngine of Haystack.
To use it, specify this engine in `settings.py`:

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'multilingual.elasticsearch_backend.ElasticsearchMultilingualSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'myproject',
        },
    }
