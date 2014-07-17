Entity
======

.. _Base: http://www.base.gov.pt/base2

This document provides the API references for the entities in the database.

.. currentmodule:: contracts

API
----

.. class:: models.Entity

    An entity is any company or institution that is enrolled in the database that are related
    trough :class:`contracts <models.Contract>`.

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

        Returns the total earned, in € cents, a value stored in :class:`~models.EntityData`.

    .. method:: total_expended()

        Returns the total expended, in € cents, a value stored in :class:`~models.EntityData`.

    .. method:: get_base_url()

        Returns the url of this entity in Base_.

    .. method:: get_absolute_url()

        Returns the url of this entity on this website.

    And the following setters:

    .. method:: compute_data()

        Computes two aggregations and stores them in its EntityData:

        #) the total value in € of the contracts where it is a contractor
        #) the total value in € of the contracts where it is contracted

        This method is used when the crawler updates new contracts.

.. class:: models.EntityData

    Data of an entity that is not retrieved from Base, i.e, it is computed with existing data.
    It is a kind of cache, but more persistent. This may become a proper cache in future.

    It has a OneToOne relationship with :class:`~models.Entity`.

    As the following attributes:

    .. attribute:: total_earned

        The money, in cents, the entity earned so far.

    .. attribute:: total_expended

        The money, in cents, the entity expended so far.
