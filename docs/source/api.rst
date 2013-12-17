API Reference
==============

In this project we use Django, a Python framework, to build a database driven (portuguese) website
to analyse and visualize the database of portuguese public contracts.

This part of the documentation focus on the API for accessing and using the database.
It documents what objects the database contains, and how you can interact with them.

Public contracts uses Django ORM to build, maintain and query a Mysql database.
This has two immediate consequences:

    1. If you don't know Django but you know mysql, you can access it (see :docs:`tools/database` for connecting to it).
    2. If you don't know mysql, you can use make virtually any query with Django and Python.

.. toctree::
   :maxdepth: 1

   api/contract
   api/entity
   api/category
