Website
=======

This documentation assumes you know Django.

Dependencies for the website
----------------------------

Install the :doc:`dependencies for the API <installation>`, plus:

memcache
^^^^^^^^

Our website uses a cache system, memcache. You can install it using::

    pip install python-memcached

Running the website
-------------------

Once you have the dependencies installed, you can run it using::

    python manage.py runserver

and enter in the url 127.0.0.1:8000.

.. _`mailing list`: https://groups.google.com/forum/#!forum/public-contracts

If you have any question, please drop by our `mailing list`_ so we can help you.
