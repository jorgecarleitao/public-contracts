Website
===============

This documentation assumes you know Django.

Dependencies for the website
----------------------------------

Install the :doc:`dependencies for the API <installation>`, plus:

memcache
^^^^^^^^^^^^^^^^^

Our website uses a cache system, memcache. You can install it using::

    pip install python-memcached

Running the website
--------------------------

Once you have the dependencies installed, you can try it by running

    python manage.py runserver

.. _`mailing list`: https://groups.google.com/forum/#!forum/public-contracts

If some problem occur, please drop by our `mailing list`_ so we can help you.


Dependencies for building the documentation
----------------------------------------------

Sphinx
^^^^^^^^^^^^^^^^^

.. _sphinx: http://sphinx-doc.org/

For building the documentation, you need sphinx_. It can be installed using::

    pip install sphinx

the documentation is built by entering in directory 'docs' and using::

    make html

