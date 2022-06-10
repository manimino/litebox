.. RangeIndex documentation master file, created by
   sphinx-quickstart on Fri May 20 21:05:57 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RangeIndex's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



Let's just do content first yeah

Functions
~~~~~~~~~

``add``

``add_many``

``find``

``find_ids``

``remove``

``update``


Why this exists
~~~~~~~~~~~~~~~

Python has excellent data structures for most problems.
Dicts, lists, tuples, heaps, and sets handle just about anything.
But there's no good answer for range queries in regular Python.

While there are plenty of B-tree and B+-tree implementations out there,
none have passed into standard use. Instead, the go-to answer when you
need a range query is to forget Python and move all your data into a
database.

Databases are great, but they are far from beautiful Pythonic
convenience. With RangeIndex, you can use a best-in-class
range query implementation directly from Python.

How it works
~~~~~~~~~~~~

RangeIndex wraps an in-memory SQLite DB. When you create a
RangeIndex with ``RangeIndex({'x': float, 'y': float})``,
a new SQLite table is created containing three columns: "x", "y", and a
third column for the Python object id. A Python object id is an integer
that uniquely identifies your Python object, akin to a pointer in C.

When you run a ``find`` that matches the row, the id is used
to locate your Python object in memory so it can be returned.

The SQLite table has an index on every column. The index on the id
column is used for fast ``remove`` and ``update`` of objects in the index.

There is no option to persist the SQLite DB to disk. This is because
the ids are memory references. When the Python program ends,
the ids no longer have any meaning.


Performance
~~~~~~~~~~~
