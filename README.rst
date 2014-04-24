Idxtools
========
.. image:: https://badge.fury.io/py/idxtools.png
    :target: http://badge.fury.io/py/idxtools
    
.. image:: https://api.travis-ci.org/emi80/idxtools.svg?branch=develop
    :target: https://travis-ci.org/emi80/idxtools

Idxtools provides some command line tools and an API to perform operations on index files.

Index files format
------------------

Index files are a sort of plain text database files to store metadata information for other files and their content. The format is as follows::

    <filepath>TAB<attributes_list>

with ``attribute_list`` as a semicolon separated list of ``key`` = ``value`` strings. Here you can find a sample line::

    /path/to/file	size=100; id=1; class=MyClass; type=MyType

Installation
============

The package can be installed either using pip::

    pip install idxtools

or from source::

    git clone https://github.com/emi80/idxtools.git
    cd idxtools
    python setup.py install
