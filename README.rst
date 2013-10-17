Introduction
============

This package provides a set of classes and methods to perform operations on index files.

Index files format
------------------

Index files are a sort of plain text database files to store metadata information for other files and their content. The format is as follows::

    <filepath>TAB<attributes_list>

with ``attribute_list`` as a semicolon separated list of ``key`` = ``value`` strings. Here you can find a sample line::

    /path/to/file	size=100; id=1; class=MyClass; type=MyType

