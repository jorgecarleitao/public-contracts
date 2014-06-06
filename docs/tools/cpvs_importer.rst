CPVS importer
=============

.. currentmodule:: cpvs

.. _Base: http://www.base.gov.pt/base2
.. _CPVS: http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
.. _tree: https://en.wikipedia.org/wiki/Tree_(data_structure)
.. _`nested set`: https://en.wikipedia.org/wiki/Nested_set_model

This section documents how we create the initial fixture for :class:`contracts.models.Category`.

Europe Union has a categorisation system for public contracts, CPVS_, that translates a string of 8 digits
into a category to be used in public contracts.

More than categories, the system builds a tree_ with broader categories like "agriculture",
and more specific ones like "potatos", see CPVS_.

In their website, they provide an <XML file `http://simap.europa.eu/news/new-cpv/cpv_2008_xml.zip`>
with all these categories. We use it to build the tree.

.. function:: build_categories(file_directory='')

    Imports the XML file and constructs the category tree, using :class:`contracts.models.Category`.

    Gets the most general categories, and saves then, repeating this recursively to more specific categories
    until it reaches the leaves of the tree.

    Assumes the file is named ``cpv_2008.xml``, and can be supplied with the directory where
    the file is.
