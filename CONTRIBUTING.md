Contributing
============

# Setup
There is a Vagrant box included in this repo to help development of the plugin.

The box contains Django, Postgres and Elasticsearch.

To boot the box simply run:

    vagrant up
    
You can access a WebGUI for elasticsearch here: http://localhost:9200/_plugin/head/


# Testing
The plugin uses Tox for testing under different Python versions.
