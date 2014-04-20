Publics
=======

.. _website: http://publicos.pt
.. _parliament: http://parlamento.pt
.. _law: http://dre.pt
.. _Base: http://www.base.gov.pt/base2

This place documents the backend of our website_.

This backend provides a consistent and homogeneous way to have complete access to three distinct portuguese databases:

- Public procurements (Base_)
- MPs and parliament procedures (parliament_)
- Law (law_)

We build and maintain an open source website and API for querying these databases.
Specifically, this project consists on the following components:

- A database in mysql and driven by Django ORM, remotely accessible.
- An API for querying the database using Django and Python.
- A website for visualizing the database and sharing statistical features of it.

How can you use it?
-------------------

For navigating in the database and discover some of its features, you can visit the website_.

.. _GitHub: https://github.com/jorgecarleitao/public-contracts

For using the API, you must first :doc:`install it <installation>`.
This is its documentation, and examples of usage can be found in the section
:doc:`ask your own questions to the database <usage>`.
