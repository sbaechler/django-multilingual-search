Contributing
============

# Setup
There is a Vagrant box included in this repo to help development of the plugin.

The box contains Django, Postgres and Elasticsearch.

To work with the box simply run:

    vagrant up
    vagrant ssh
    
create a virtualenv and install the requirements in `tests/testproject/requirements.txt`.
    
You can access a WebGUI for elasticsearch here: http://localhost:9200/_plugin/head/


# Testing
The plugin uses Tox for testing under different Python versions.


# Dataset

https://archive.ics.uci.edu/ml/datasets/Reuters+RCV1+RCV2+Multilingual,+Multiview+Text+Categorization+Test+collection