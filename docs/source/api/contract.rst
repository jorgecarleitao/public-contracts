Contract
=========

.. _Base: http://www.base.gov.pt/base2

This document provides the API references for the contracts in the database.

.. currentmodule:: contracts

API
------

.. class:: models.Contract

    A contract is a relationship between :doc:`entities <entity>` enrolled in the database.
    Each contract has a set of contractors (who paid), and contracted, along with other information about it.

    All the fields of this model are retrieved from Base_ using the :doc:`crawler`. Except for :attr:`base_id`
    and :attr:`added_date`, all entries can be null if they don't exist in
    Base_. They are:

    .. attribute:: description

        The description of the contract.

    .. attribute:: price

        The price of the contract, in cents (to an integer).

    .. attribute:: category

        A Foreign key to the contract's :doc:`category`.

    .. attribute:: contractors

        A ManyToMany relationship to :doc:`entities <entity>`. Related name "contracts_made".

    .. attribute:: contracted

        A ManyToMany relationship to :doc:`entities <entity>`.

    .. attribute:: added_date

        The date it was added to Base_ database.

    .. attribute:: signing_date

        The date is was signed (?).

    .. attribute:: close_date

        The date is was closed (?).
        It is normally null.

    .. attribute:: base_id

        The primary key of the contract on the Base_ database.
        It is "unique".

    .. attribute:: contract_type

        A Foreign key to one of the types of contracts.

    .. attribute:: procedure_type

        A Foreign key to one of the types of procedures.

    .. attribute:: contract_description

        A text about the object of the contract (i.e. what was bought or sold).

    .. attribute:: country
    .. attribute:: district
    .. attribute:: council

        Country, district, council.

    This model has a getter:

    .. method:: get_absolute_url()

        Returns the url of this entity in Base_.
