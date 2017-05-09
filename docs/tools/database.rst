Database
========

This document explains what is our database, how you can access it remotely,
and how you can obtain a dump of it.

Database
--------

.. _`official database`: http://www.base.gov.pt/base2

Our database contains all the information the official databases contains. Additionally, our database is bound
to a database ORM and web framework - Django - that facilitates its :doc:`usage`.

Either by using Django or not, you have full remote access (read only) to it.

Remote connection
-----------------

You can access our database using:

- database: publics
- username: publics_read_only
- password: read-only
- host: 185.20.49.8
- port: 5432

Create dumps
------------

In the terminal, run::

    pg_dump -h 185.20.49.8 -p 5432 -U publics_read_only -d publics > dump.sql

This creates a file "dump.sql" (it can take a while) that you can load to a database in your own computer.
