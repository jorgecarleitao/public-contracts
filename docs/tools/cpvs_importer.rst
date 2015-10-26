CPVS importer
=============

.. currentmodule:: contracts.tools.cpvs

.. _CPVS: http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
.. _tree: https://en.wikipedia.org/wiki/Tree_(data_structure)
.. _`nested set`: https://en.wikipedia.org/wiki/Nested_set_model
.. _`XML file`: http://simap.europa.eu/news/new-cpv/cpv_2008_xml.zip

This section documents how we create the initial fixture for
:class:`categories <contracts.models.Category>`.

Europe Union has a categorisation system for public contracts, CPVS_, that
translates a string of 8 digits into a category to be used in public contracts.

More than categories, this system builds a tree with broader categories like
"agriculture", and more specific ones like "potatos".

They provide the fixture as an `XML file`_, which we import:

.. function:: build_categories()

    Constructs the category tree of :class:`categories <contracts.models.Category>`.

    Gets the most general categories and saves then, repeating this recursively
    to more specific categories until it reaches the leaves of the tree.

    The official categories are retrieved from the internet.
