# coding: utf-8
from distutils.core import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Hard linking doesn't work inside VirtualBox shared folders. This means that
# you can't use tox in a directory that is being shared with Vagrant,
# since tox relies on `python setup.py sdist` which uses hard links. As a
# workaround, disable hard-linking if setup.py is a descendant of /vagrant.
# See
# https://stackoverflow.com/questions/7719380/python-setup-py-sdist-error-operation-not-permitted
# for more details.
if os.path.abspath(__file__).split(os.path.sep)[1] == 'vagrant':
    del os.link

setup(
    name='django-multilingual-search',
    version='2.3.0.beta',
    packages=['multilingual'],
    url='https://github.com/sbaechler/django-multilingual-search',
    license='BSD',
    author='Simon Bächler',
    author_email='sb@feinheit.ch',
    description='A drop-in replacement for the Haystack Elasticsearch backend which allows '
                'multilingual indexes for Django.',
    long_description=read('README.md'),
    platforms=['OS Independent'],
    # install_requires=[
    #     'Django>=1.5',
    #     'haystack==2.3.1',
    #     'elasticsearch=>1.5.0'
    # ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
