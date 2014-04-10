Publics
=======

.. _website: http://publicos.pt
.. _parliament: http://parlamento.pt
.. _law: http://dre.pt
.. _Base: http://www.base.gov.pt/base2

This place documents the backend of our website_.

The website provides a consistent and homogeneous way to have complete access to three distinct portuguese databases:

- Public procurements (Base_)
- MPs and parliament procedures (parliament_)
- Law (law_)

We build and maintain an open source website and API for querying the these databases.
Specifically, this project consists on the following components:

- A database driven by Django ORM for such databases, remotely accessible.
- An API for querying the database using Django and Python.
- A website for visualizing the database and sharing statistical features of it.

How can I use it?
-----------------

For navigating in the database and discovering some of its features, visit our website_.

.. _GitHub: https://github.com/jorgecarleitao/public-contracts

For using the API, you can download the source, available on GitHub_.
This is its documentation, and examples of usage can be found in the section
:doc:`ask your own questions to the database <usage>`.
