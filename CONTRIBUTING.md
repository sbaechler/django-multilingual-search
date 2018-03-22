Contributing
============

Feel free to contribute to the project. It is hosted on
[Github](https://github.com/sbaechler/django-multilingual-search).
Clone the repository and open a pull request.

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

To manually run the tests, activate a virtual env, go to the directory /vagrant/tests
and run ``./testproject/manage.py test``.


# Test Data
The app uses the Europarl ACL WMT 2013 test set.

http://matrix.statmt.org/test_sets/list

http://matrix.statmt.org/test_sets/newstest2013.tgz?1367361979

There is a Django management command that can import the reference SGML data and create Django models from it.

    vagrant@precise64:/vagrant/tests/testproject$ ./manage.py import_sgm --delete ../../test

The option ``--delete`` causes the import to delete any existing data.
The only argument is the path to the ``test`` directory containing the SGML files.

The ACL WMT 2013 test set is included as Django-fixture.


# Coding style
PEP-8 with a line length of 100.

If you have the [Editorconfig Plugin](http://editorconfig.org/) installed, your IDE is
automatically going to enforce the correct style.
