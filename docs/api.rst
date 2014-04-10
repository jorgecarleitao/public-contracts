API Reference
=============

This part of the documentation focus on the API for accessing and using the database.
It documents what objects the database contains, and how you can interact with them.

Publics uses Django ORM to build, maintain and query a Mysql database.
This has two immediate consequences:

    1. If you don't know Django but you know mysql, you can access it (see :doc:`tools/database` for connecting to it).
    2. If you don't know mysql, but you know python, you can make queries using this API.

.. toctree::
   :maxdepth: 1

   contracts_api/contract
   contracts_api/entity
   contracts_api/category
   deputies_api/legislature
   deputies_api/deputy
   deputies_api/mandate
   deputies_api/party
