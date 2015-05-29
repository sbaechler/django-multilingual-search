# coding: utf-8
from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-multilingual-search',
    version='0.1.0',
    packages=['multilingual'],
    url='https://github.com/sbaechler/django-multilingual-search',
    license='BSD',
    author='Simon Bächler',
    author_email='sb@feinheit.ch',
    description='A drop-in replacement for the Haystack Elasticsearch backend which allows '
                'multilingual indexes for Django.',
    long_description=read('README.md'),
    platforms=['OS Independent'],
    install_requires=[
        'Django>=1.4',
        'haystack',
        'elasticsearch=>1.5.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
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
