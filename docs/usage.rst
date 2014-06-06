Asking questions to the database
================================

This tutorial assumes you already :doc:`installed <installation>` the source.

.. _Django: https://www.djangoproject.com/
.. _queries: https://docs.djangoproject.com/en/dev/topics/db/queries/
.. _Django queries API: https://docs.djangoproject.com/en/dev/ref/models/querysets/
.. _models: https://docs.djangoproject.com/en/dev/topics/db/models/

We assume you are in directory "contracts", as the installation part ended there,
and that you start a Python session from there (e.g. enter "python" in the terminal).

Setup
-----

To use Django_, we have to setup it first. In the module ``set_up`` in package tools,
we provide a function to that, which we now use::

    >>> from tools.set_up import set_up_django_environment
    >>> set_up_django_environment('tools.settings')

This sets up a minimal Django environment using the settings file ``tools/settings.py``.

Accessing the database
----------------------

In this API, objects are Django models_, which we need to import::

    >>> from contracts import models

.. _`this contract`: http://www.base.gov.pt/base2/html/pesquisas/contratos.shtml#791452

Look at `this contract`_ in the official database. It has the number "791452". Lets pick it up::

    >>> contract = models.Contract.objects.get(base_id=791452)

Now, lets start with its price::

    >>> print(contract.price)

and its description::

    >>> print(contract.description)

.. _ManyToMany: https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_many/

Lets now pick the entity that made this contract. In this case there is only one, but in general
there can be more: a contract has a ManyToMany_ relationship with entities because each contract can have several
entities (a joint contract), but also each entity can have several contracts.

In fact, each contract has two ManyToMany: the entities that paid, and the entities that were paid.

Lets say we want the entity that paid this contract. In that case, we pick the set of all entities that paid,
and select the first one::

    >>> entity = contract.contractors.all()[0]
    >>> print(entity)

Let's now pick the contracts that this entity made. To that, we use the "contracts_made" of the entity::

    >>> entity_contracts = entity.contracts_made.all()

.. _count: https://docs.djangoproject.com/en/dev/ref/models/querysets/#count

Lets count_ the number of these contracts::

    >>> print(entity_contracts.count())

.. _can check: http://www.base.gov.pt/base2/html/pesquisas/entidades.shtml#23537

You `can check`_ that this number matches the number in the official database.
(there can be small error when there were contracts added today;
our database is synchronized in the end of the day).

Now, how much is the price of all those contracts?

.. _aggregate: https://docs.djangoproject.com/en/dev/topics/db/aggregation/

To answer that, we have to aggregate the prices. The `syntax <aggregate>`_ in Django
is the following::

    >>> from django.db.models import Sum
    >>> total_price = entity_contracts.aggregate(our_sum=Sum('price'))['our_sum']
    >>> print(total_price)

Again, you `can check`_ on the official website.

As a final example, we are going to use a filter. Lets say you want all the above
contracts, but restricted to prices higher than 10.000€. For this, we need to "filter" these contracts::

    >>> expensive_contracts = entity_contracts.filter(price__gt=10000*100)
    >>> print(expensive_contracts.count())

The "price__gt" means price `(g)reater (t)han <Django queries API>`_, and we multiply by 100 because
:attr:`prices are in euro cents <models.Contract.price>`.

For now, that's it. You now have the minimal knowledge to ask your own questions. In section :doc:`here <api>`
you can find references of all models.

Notes:

 - The syntax we use here (e.g. "contracts_made") **is** Django API.
 - If you don't know Django, you can look at the existing source code of the website and copy from it.
 - The API documentation is still not complete. You can find it :doc:`here <api>` or :doc:`help <contribute>` finishing it.

.. _mailing list: https://groups.google.com/forum/#!forum/public-contracts

In any case, if you need help, drop by our `mailing list`_.
