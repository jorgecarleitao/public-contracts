Asking questions to the database
==================================

This tutorial assumes you already :doc:`installed <installation>` the source.

.. _Django: https://www.djangoproject.com/
.. _queries: https://docs.djangoproject.com/en/1.6/topics/db/queries/
.. _queries API: https://docs.djangoproject.com/en/1.6/ref/models/querysets/
.. _models: https://docs.djangoproject.com/en/dev/topics/db/models/

We use Django_ for accessing the database. Django is a web framework,
but here we limit the usage of Django to accessing the database.

We will assume you are in directory "contracts/tools", as the installation part ended there.

Setup
---------

In Python, to use a package, we have to import it.
To use Django, we have to setup it first. In this tutorial we will skip this part since it is very technical.
Assume the setup we provide is correct::

    import set_up
    set_up.set_up_django_environment()

Accessing the database
----------------------

Django is setup, we are ready to use it.

In Django, models_ are Python classes that can be represented in the database.
We need to import the models for this API::

    from contracts import models

with this, you have just gained a piece of intellectual freedom:

From now on, each contract, entity or category is an instance of a Python class,
and we can access its data using standard Python notation for a class.

But how do we pick a contract from the database?

.. _`this contract`: http://www.base.gov.pt/base2/html/pesquisas/contratos.shtml#791452

Look at `this contract`_ in the official database. It has the number "791452". Lets pick it up::

    contract = models.Contract.objects.get(base_id=791452)

good, now, what do we want to know about the contract? Lets start with its price::

    print contract.price

Its kind of powerful right? (see also :doc:`responsibility <code_of_conduct>`). Now its category::

    print contract.category

.. _ManyToMany: https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_many/

Lets now pick the entity that made this contract. Well, in this case there is only one, but in general
there can be more: a contract has a ManyToMany_ relationship with entities because each contract can have several
entities (a joint contract), but also each entity can have several contracts.

In fact, each contract has two many to many: the entities that paid, and the entities that were paid.
Why would you care? Because you have to tell python which ones you want.

Lets say we want the entity that paid contract 791452. In that case, we pick the set of all entities that paid,
and just choose the first one::

    entity = contract.contractors.all()[0]
    print entity

Good. Let's see the contracts this entity paid. To that, we use the "contracts_made" of the entity.

    entity_contracts = entity.contracts_made.all()

Lets count the number of these contracts:

    print entity_contracts.count()

.. _can check: http://www.base.gov.pt/base2/html/pesquisas/entidades.shtml#23537

You `can check`_ that the number matches the number in the official database.
(there can be an error of 1 or 2 when there were contracts added today;
our database is only synchronized in the end of the day).

Ok, now a more difficult question: how much is the price of all those contracts?

.. _aggregate: https://docs.djangoproject.com/en/dev/topics/db/aggregation/

To answer that, we have to use aggregate_: we are aggregating a result over a set of contracts. The syntax
is the following::

    from django.db.models import Sum

    total_price = entity_contracts.aggregate(our_sum=Sum('price'))['our_sum']
    print total_price

Remember calling "contract.price" before? Well, this is doing almost the same:
we are aggregating the sum of all contract prices, which we call "our_sum", and them
we get our sum (...)['our_sum'] back. Again, you `can check`_.

As a final example, we are going to use a filter. Lets say you want all the above
contracts, but restricted to prices higher than 10.000€. For this, we need to "filter" the contracts::

    expensive_contracts = entity_contracts.filter(price__gt=10000*100)  # *100 because prices are in euro cents.
    print expensive_contracts.count()

The "price__gt" means price (g)reater (t)han. The full set of options can be found in Django queries_.

.. _mailing list: https://groups.google.com/forum/#!forum/public-contracts

If you need any help, drop by our public `mailing list`_.

That's it. From now on, the boundaries are only limited by those of your imagination...
