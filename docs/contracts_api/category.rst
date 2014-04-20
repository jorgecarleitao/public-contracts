Category
========

.. currentmodule:: contracts

.. _Base: http://www.base.gov.pt/base2

This document provides the API references for the categories of contracts in the database.

From CPVS to categories
-----------------------

.. _CPVS: http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
.. _tree: https://en.wikipedia.org/wiki/Tree_(data_structure)
.. _`nested set model`: https://en.wikipedia.org/wiki/Nested_set_model

Europe Union has a categorisation system for public contracts, CPVS_, that maps a string of 8 digits
into a category (i.e. a name) to be used in each public contract.

More than categories, the system builds a tree_ with broader categories like "agriculture",
and more specific ones like "potatos".

In our database, we construct a tree (using a `nested set model`_) of categories, and abstract the idea of digits:
each category has a parent, a depth, and child categories.

Each contract in Base_ has one (or none) of such CPVS and thus, each contract is
:attr:`associated <models.Contract.category>` with one (or none) category.

API
------

.. class:: models.Category

    A category is an OneToMany relationship to :class:`~models.Contract`: each contract has one category,
    each category can have more than one contract. This relationship is thus defined in the contract model.

    It has the following attributes:

    .. attribute:: code

        The CPVS_ code of the category.

    .. attribute:: description_en
    .. attribute:: description_pt

        The official descriptions of the category in english and portuguese, respectively.

    .. attribute:: depth

        The depth of the attribute on the tree.

    And has the following methods:

    .. method:: get_children()

        Returns all children categories.

    .. method:: get_ancestors()

        Returns all anscestor categories, excluding itself.

    .. method:: get_absolute_url()

        Returns the url of this category in the website.

    .. method:: own_contracts()

        Returns all contracts that specifically belong to this category (i.e. have same CPVS code).

    .. method:: contracts()

        Returns all contracts that belong to either this category or any of its children.

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
