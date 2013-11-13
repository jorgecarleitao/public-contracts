Installation
=============

This document explains how you can install the tools this project provides.

.. _pip: https://pypi.python.org/pypi/pip

We assume you know a little of Python and how to install Python packages in your computer using pip_.

.. _virtualenv: http://www.virtualenv.org/en/latest/

.. note:: You may need privileges to install using 'pip ...', in this case, you must use 'sudo pip ...' instead.

.. hint:: You may want to use virtualenv_ to create a clean python environment that avoids installing the packages system-wise.

Getting the source
---------------------

.. _GitHub: https://github.com/jorgecarleitao/public-contracts
.. _downloaded: https://github.com/jorgecarleitao/public-contracts
.. _mailing-list: https://groups.google.com/forum/#!forum/public-contracts

The source can be downloaded_ from GitHub, or cloned from the repository (also in GitHub_).

Dependencies of the database API
----------------------------------

Django
^^^^^^^^^^^^^^^^^

Use::

    pip install Django

mysql-python
^^^^^^^^^^^^^^^^^

Because we use mysql, you have to install the bindings for Python. Use::

    pip install mysql-python

treebeard
^^^^^^^^^^^^^^^^^

We use this package for efficient storage and usage of :doc:`tree structures <api/category>` in the database.
Install using::

    pip install django-treebeard

Running the database API
--------------------------

Once you have the dependencies installed, run::

    cd tools
    python example.py

If some problem occur, please drop by our mailing-list_ so we can help you.

For more information on the API, see section :doc:`usage` for a tutorial, and section :doc:`API` for its complete
documentation.

Dependencies for the website
----------------------------------

Install the dependencies for the API, plus:

memcache
^^^^^^^^^^^^^^^^^

Our website uses a cache system, memcache. You can install it using::

    pip install python-memcached

Running the website
--------------------------

Once you have the dependencies installed, you can try it by going to the directory "tools", and running

    python manage.py runserver

If some problem occur, please drop by our mailing-list_ so we can help you.


Dependencies for building the documentation
----------------------------------------------

Sphinx
^^^^^^^^^^^^^^^^^

.. _sphinx: http://sphinx-doc.org/

For building the documentation, you need sphinx_. It can be installed using::

    pip install sphinx

the documentation is built by entering in directory 'docs' and using::

    make html

