Setting up the project for development
======================================

The project contains a Vagrantfile which sets up a machine with Elasticsearch and Django.

Elasticsearch
-------------

You can access the Web-Interface of Elasticsearch at http://localhost:9200/_plugin/head/


Testing
-------

To run the tests, go to the directory /vagrant/tests and run ``./testproject/manage.py test``.


Test Data
---------

The app uses the Europarl ACL WMT 2013 test set.

http://matrix.statmt.org/test_sets/list

http://matrix.statmt.org/test_sets/newstest2013.tgz?1367361979

There is a Django management command that can import the reference SGML data and create Django models from it.

    vagrant@precise64:/vagrant/tests/testproject$ ./manage.py import_sgm --delete ../../test

The option ``--delete`` causes the import to delete any existing data.
The only argument is the path to the ``test`` directory containing the SGML files.

The ACL WMT 2013 test set is included as Django-fixture.
