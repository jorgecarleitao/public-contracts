Category
========

.. _Base: http://www.base.gov.pt/base2

This document provides the API references for the categories of contracts in the database.

For information on building the database of categories, see :mod:`contracts.cpvs`.

.. currentmodule:: contracts

From CPVS to categories
-------------------------

.. _CPVS: http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
.. _tree: https://en.wikipedia.org/wiki/Tree_(data_structure)
.. _`nested set`: https://en.wikipedia.org/wiki/Nested_set_model

Europe Union has a categorisation system for public contracts, CPVS_, that translates a string of 8 digits
into a category to be used in public contracts.

More than categories, the system builds a tree_ with broader categories like "agriculture",
and more specific ones like "potatos". For more information, see CPVS_.

In our database, we construct a tree (a `nested set`_, specifically) of categories, and abstract the idea of digits:
each category has a parent, a depth, and child categories (see :doc:`tools/cpvs_importer`).

Each contract in Base_ has one (or none) of these numbers. In our database, each contract is
:attr:`associated <models.Contract.category>` with one (or none) category.
category.

API
------

.. class:: models.Category

    A category is an OneToMany relationship to :doc:`contract`: each contract has one category, each category
    as more than one contract.

    It has the following attributes:

    .. attribute:: code

        The CPVS_ code of the category.

    .. attribute:: description_en
    .. attribute:: description_pt

        The official descriptions of the category in portuguese and english, respectively.

    .. attribute:: depth

        The depth of the attribute on the tree.

    And has the following methods:

    .. method:: get_absolute_url()

        Returns the url of this category in the website.

    .. method:: own_contracts()

        Returns all contracts that belong to this category (i.e. have same CPVS code).

    .. method:: contracts()

        Returns all contracts that belong to this category or to any of its children.

    .. method:: own_contracts_count()
    .. method:: contracts_count()

        Counts the contracts that:
            belong to this category

            belong to this category or any of its children.

    .. method:: own_contracts_price()
    .. method:: contracts_price()

        Sums the prices of the contracts that:
            belong to this category

            belong to this category or any of its children.
