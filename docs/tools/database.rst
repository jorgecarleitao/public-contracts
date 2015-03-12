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
- username: publics
- password: read-only
- host: 5.153.9.51
- port: 5432

.. _`phpmyadmin panel`: https://web306.webfaction.com/static/phpMyAdmin

You can also take a look at it in `phpmyadmin panel`_, using the same credentials.

Create dumps
------------

In the terminal, run::

    pg_dump -h 5.153.9.51 -p 5432 -U publics_read_only -W read-only -d publics > dump.sql

This creates a file "dump.sql" (it can take a while) that you can load to a database in your own computer.
