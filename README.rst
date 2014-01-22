Idxtools
========
.. image:: https://badge.fury.io/py/idxtools.png
    :target: http://badge.fury.io/py/idxtools

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

Changelog
=========

Version 0.9:
    - Add option to remove command to clear metadata and modify cli to remove multiple files (`#1 <https://github.com/emi80/idxtools/issues/1>`_ and `#2 <https://github.com/emi80/idxtools/issues/2>`_)
    - Update show command to support ids for replicates (`#5 <https://github.com/emi80/idxtools/issues/5>`_)
    - Update signal handler for SIGPIPE (`#7 <https://github.com/emi80/idxtools/issues/7>`_)
    - Use logging module (`#6 <https://github.com/emi80/idxtools/issues/6>`_)

Version 0.9b1:
    - Initial release
