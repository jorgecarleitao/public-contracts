Installation
=============

This document explains how you can install the API for accessing our database.

.. _pip: https://pypi.python.org/pypi/pip

We assume you know a little of Python and how to install Python packages in your computer using pip_.

.. _virtualenv: http://www.virtualenv.org/en/latest/

.. note:: You may need privileges to install using 'pip ...'. If that is the case, you must use 'sudo pip ...' instead.

Getting the source
---------------------

.. _GitHub: https://github.com/jorgecarleitao/public-contracts
.. _downloaded: https://github.com/jorgecarleitao/public-contracts/archive/master.zip
.. _mailing-list: https://groups.google.com/forum/#!forum/public-contracts

The source can be downloaded_ from GitHub, or cloned from the repository (also in GitHub_).
The source doesn't need to be installed: once you downloaded it, it is ready for use.

Dependencies
--------------

For accessing the API, you need to install three python packages.

Django
^^^^^^^^^^^^^^^^^

We use Django to abstract ourselves of the idea of database, and use Python classes to work with the database::

    pip install Django

mysql-python
^^^^^^^^^^^^^^^^^

Our remote database is in mysql. To Python communicate with it, we need a binding::

    pip install mysql-python

treebeard
^^^^^^^^^^^^^^^^^

The categories in our database are organized in a :doc:`tree structures <api/category>`.
We use a package to an efficiently storage them in our database, and this package provides you the way to use them.

Install using::

    pip install django-treebeard

Running the database API
--------------------------

.. _official number: http://www.base.gov.pt/base2/html/pesquisas/contratos.shtml

Once you have the dependencies installed, enter in its directory and run::

    cd tools
    python example.py

If everything went well, it outputs two numbers:

    1. the total number of contracts in the database, that you can corroborate with the `official number`_.
    2. the value of all contracts in the database.

If some problem occur, please drop by our mailing-list_ so we can help you.

For more information on the API, see section :doc:`usage` for a tutorial, and section :doc:`API` for its complete
documentation.
