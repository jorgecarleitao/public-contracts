API Reference
=============

This part of the documentation focus on the API for accessing and using the database.
It documents what objects the database contains, and how you can interact with them.

Publics uses Django ORM to build, maintain and query a Postgres database.
This has two immediate consequences:

    1. If you don't know python/Django but you know SQL, you can access it remotely (see :doc:`tools/database`).
    2. If you don't know SQL, but you know Python and/or Django,
       you can take advantage of this API (see :doc:`/usage`)

.. toctree::
   :maxdepth: 1

   contracts_api/contract
   contracts_api/entity
   contracts_api/category
   deputies_api/legislature
   deputies_api/deputy
   deputies_api/mandate
   deputies_api/party
