Installation
============

This document explains how you can install the API for *accessing* the database.
To deploy the website, see :doc:`website/website`.

.. _pip: https://pypi.python.org/pypi/pip

We assume you know a little of Python and know how to install Python packages
in your computer using pip_.

Getting the source
------------------

.. _GitHub: https://github.com/jorgecarleitao/public-contracts
.. _downloaded: https://github.com/jorgecarleitao/public-contracts/archive/master.zip
.. _mailing-list: https://groups.google.com/forum/#!forum/public-contracts

The source can be either downloaded_ or cloned from the GitHub_ repository using::

    git clone https://github.com/jorgecarleitao/public-contracts.git

Like most Python code, the source doesn't need to be installed; you just have to
put it somewhere in your computer.

You need Python 3.

Dependencies
------------

For using the code, you need to install three python packages:

Django
^^^^^^

We use Django ORM to abstract ourselves of the idea of database and use Python
classes to work with the data::

    pip install Django

Postgres
^^^^^^^^

Our remote database is in postgres. To Python communicate with it, we need a
binding::

    pip install psycopg2

treebeard
^^^^^^^^^

The categories in the database are organized in a :doc:`tree structure
<contracts_api/category>`. We use django-treebeard to efficiently storage them
in our database.

Install using::

    pip install django-treebeard

Running the example
-------------------

.. _official number: http://www.base.gov.pt/base2/html/pesquisas/contratos.shtml

Once you have the dependencies installed, enter in its directory and run::

    python -m contracts.tools.example

If everything went well, it outputs two numbers:

    1. the total number of contracts in the database, that you can corroborate
       with the `official number`_.
    2. the sum of the values of all contracts.

If some problem occur, please add an [issue](https://github.com/jorgecarleitao/public-contracts/issues)
so we can help you and improve these instructions.

From here, you can see section :doc:`usage` for a tutorial, and section
:doc:`api` for the complete documentation.
