Our database
=============

This document explains what is our database, how you can access it remotely,
and how you can obtain and use a dump of it.

Database
---------------

.. _`official database`: http://www.base.gov.pt/base2

The `official database` doesn't provide access to their database (for a good reason), but provides
access to its data. On one hand, this means we cannot perform any query we want, but on the other, it means we
can retrieve its information.

Thus, we use a :doc:`crawler <crawler>` to retrieve its information and we create our own database from their data
to allow querying.

Our database contains all the information the official database contains. Additionally, our database is binded
to a database handler and web framework - Django - that facilitates its :doc:`usage` using Python.

Because it is inefficient to have a own database for each code, we provide remote access to ours.

Remote connection
------------------

You can access our database using:

- database: contracts
- username: public_contracts
- password: read-only
- host: 5.153.9.51
- port: 3306

As the password suggests, the access is read only. If you want to change the database,
you can either :doc:`contribute <contribute>` to this project,
or you can download a dump and import it to your own database.

Download and import dumps
--------------------------

.. important:: This is not implemented yet.

We provide dumps of the database in .sql. These dumps can be used for instance to mount the database locally.
