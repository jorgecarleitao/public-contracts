Entity
======

.. _Base: http://www.base.gov.pt/base2

This document provides the API references for the entities in the database.

.. currentmodule:: contracts

API
----

.. class:: models.Entity

    An entity is any company or institution that is enrolled in the database.

    All the fields of this model are directly retrieved from Base_.
    They are:

    .. attribute:: name

        The name of the entity.

    .. attribute:: base_id

        The primary key of the entity on the Base_ database. It is "unique".

    .. attribute:: nif

        The fiscal identification number of the entity.

    .. attribute:: country

        The country it is registered. It may be "null" when there is no such information.

    It has the following getters:

    .. method:: total_earned()

        Returns the total earned, in €, a value stored in :class:`~models.EntityData`.

    .. method:: total_expended()

        Returns the total expended, in €, a value stored in :class:`~models.EntityData`.

    .. method:: get_absolute_url()

        Returns the url of this entity in Base_.

    .. method:: count_contracts()

        Returns the number of contracts this entity is a contractor.

    And the following setters:

    .. method:: compute_data()

        Computes two aggregations and stores them in its EntityData:

        #) the total value in € of the contracts where it is a contractor
        #) the total value in € of the contracts where it is contracted

        This method is used when the crawler updates new contracts.

    .. method:: add_contract_as_contractor(contract)

        Updates its data expenses by adding contract's value.

    .. method:: add_contract_as_contracted(contract)

        Updates its data earnings by adding contract's value.

    While :meth:`compute_data` computes the totals by summing all contract's value,
    :meth:`add_contract_as_contractor` and :meth:`add_contract_as_contracted` updates
    the totals with using the information of one contract.


.. class:: models.EntityData

    Data of an entity that is not retrieved from Base, i.e, it is computed with existing data.
    It is a kind of cache, but more persistent. This may become a proper cache in future.

    It has a OneToOne relationship with :class:`~models.Entity`.

    As the following attributes:

    .. attribute:: total_earned

        The money, in cents, the entity earned so far.

    .. attribute:: total_expended

        The money, in cents, the entity expended so far.

Usage
-----

Because an entity is a subclass of a Django model, you can retrieve
information about it using Django's ORM principle.

For instance, if you want to select a specific entity by a NIF, you can use::

    from contracts.models import Entity

    entity = Entity.objects.get(nif=12345678)

if you want to know all the contracts it already made, you can use::

    contracts = entity.contracts_made.all()

if you want to know the total expenses of the entity, you can use::

    total_expenses = contracts.aggregate(total=Sum('price'))['total']

    # or

    total_expenses = entity.total_expenses()

