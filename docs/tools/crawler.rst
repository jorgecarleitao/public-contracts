Crawler for Contracts and Tenders
=================================

.. currentmodule:: contracts.crawler

.. _Base: http://www.base.gov.pt/base2
.. _requests: http://docs.python-requests.org/en/latest/

This document explains how Base_ provides its data and how the crawler works.

.. important::
    Please, take precautions on using the crawler as it can generate Denial of
    Service (DoS) to Base_ database. We provide remote access to our database to
    avoid that.

.. important::
    Crawling Base_ from scratch takes more than 2 days as of Jan. 2014.

Base database
-------------

Base_ uses the following urls to expose its data

1. :class:`~contracts.models.Entity`: http://www.base.gov.pt/base2/rest/entidades/[base_id]
2. :class:`~contracts.models.Contract`: http://www.base.gov.pt/base2/rest/contratos/[base_id]
3. :class:`~contracts.models.Tender`: http://www.base.gov.pt/base2/rest/anuncios/[base_id]
4. List of :class:`~contracts.models.Country`: http://www.base.gov.pt/base2/rest/lista/paises
5. List of :class:`~contracts.models.District`: http://www.base.gov.pt/base2/rest/lista/distritos?pais=[country_base_id]; (portugal_base_id=187)
6. List of :class:`~contracts.models.Council`: http://www.base.gov.pt/base2/rest/lista/concelhos?distrito=[district_base_id];
7. List of :class:`~contracts.models.ContractType`: http://www.base.gov.pt/base2/rest/lista/tipocontratos
8. List of :class:`~contracts.models.ProcedureType`: http://www.base.gov.pt/base2/rest/lista/tipoprocedimentos

Each url returns ``json`` with information about the particular object.
For this reason, we have an abstract crawler for retrieving this information
and map it to this API.

What the crawler does
---------------------

The crawler accesses Base_ urls using the same procedure for entities, contracts
and tenders. It does the following:

1. retrieves the list ``c1_ids=[i*10k, (i+1)*10k]`` of ids from links 4., 5. or 6.;
2. retrieves all ids in range ``[c_ids[0], c_ids[-1]]`` from our db, ``c2_ids``
3. Adds, using links 1.,2. or 3. all ids in ``c1_ids`` and not in ``c2_ids``.
4. Removes, using links 1.,2. or 3. all ids in ``c2_ids`` and not in ``c1_ids``.
5. Go to 1 with ``i += 1`` until it covers all contracts.

The initial value of ``i`` is 0 when the database is populated from scratch, and is
such that only one cycle 1-5 is performed when searching for new items.

API references
--------------

This section introduces the different crawlers we use to crawl Base_.

.. class::JSONCrawler

    Uses a session to get responses from urls.

    .. method:: get_response(url, headers=None)

        Returns the response of a GET request with optional headers

    .. method:: get_json(url, headers=None)

        Returns a dictionary corresponding to the json content of the url.

.. class:: ContractsStaticDataCrawler

    A subclass :class:`JSONCrawler` for static data. This crawler only needs to
    be run once and is used to populate the database the first time.

    .. method:: retrieve_and_save_all()

        Retrieves and saves all static data of contracts.

Given the size of Base_ database, and since it is constantly being updated,
contracts, entities and tenders, use the following approach:

.. class:: DynamicCrawler

    An abstract subclass of :class:`JSONCrawler` that implements the crawling
    procedure described in the previous section.

    .. attribute:: object_name = None

        A string with the name of the object used to name the ``.json`` files;
        to be overwritten.

    .. attribute:: object_url = None

        The url used to retrieve data from BASE; to be overwritten.

    .. attribute:: object_model = None

        The model to be constructed from the retrieved data; to be overwritten.

    .. staticmethod:: clean_data(data)

        Cleans ``data``, returning a ``cleaned_data`` dictionary with keys being
        fields of the :attr:`object_model` and values being extracted from
        ``data``.

        To be overwritten by subclasses.

    .. method:: save_instance(cleaned_data)

        Saves or updates an instance of type :attr:`object_model`
        using the dictionary ``cleaned_data``.

        This method can be overwritten for changing how the instance is saved.

        Returns a tuple ``(instance, created)`` where ``created`` is ``True``
        if the instance was created (and not just updated).

    .. method:: update_instance(base_id)

        Uses :meth:`get_json`, :meth:`clean_data` and :meth:`save_instance` to
        create or update an instance identified by ``base_id``.

        Returns the output of :meth:`save_instance`.

    .. method:: get_instances_count()

        Returns the total number of existing instances in BASE db.

    .. method:: get_base_ids(row1, row2)

        Returns a list of instances from BASE of length ``row2 - row1``.

    .. method:: update_batch(row1, row2)

        Updates a batch of rows, step 2.-4. of the previous section.

    .. method:: update(start=0, end=None, items_per_batch=1000)

        The method retrieves count of all items in BASE (1 hit), and
        synchronizes items from `start` until `min(end, count)` in batches
        of `items_per_batch`.

        If `end=None` (default), it retrieves until the last item.

        if `start < 0`, the start is counted from the end.

        Use e.g. `start=-2000` for a quick retrieve of new items;

        Use `start=0` (default) to synchronize all items in database
        (it takes time!)


.. class:: EntitiesCrawler

    A subclass of :class:`DynamicCrawler` to populate
    :class:`~contracts.models.Entity` table.

    Overwrites :meth:`~DynamicCrawler.clean_data` to clean data to
    :class:`~contracts.models.Entity`.

    Uses:

    * :attr:`~DynamicCrawler.object_directory`: ``'../../data/entities'``
    * :attr:`~DynamicCrawler.object_name`: ``'entity'``;
    * :attr:`~DynamicCrawler.object_url`:
      ``'http://www.base.gov.pt/base2/rest/entidades/%d'``
    * :attr:`~DynamicCrawler.object_model`: :class:`~contracts.models.Entity`.

.. class:: ContractsCrawler

    A subclass of :class:`DynamicCrawler` to populate
    :class:`~contracts.models.Contract` table.

    Overwrites :meth:`~DynamicCrawler.clean_data` to clean data to
    :class:`~contracts.models.Contract`
    and :meth:`~DynamicCrawler.save_instance` to also save ``ManytoMany``
    relationships of the :class:`~contracts.models.Contract`.

    Uses:

    * :attr:`object_directory`: ``'../../data/contracts'``
    * :attr:`object_name`: ``'contract'``;
    * :attr:`object_url`: ``'http://www.base.gov.pt/base2/rest/contratos/%d'``
    * :attr:`object_model`: :class:`~contracts.models.Contract`.

.. class:: TenderCrawler

    A subclass of :class:`DynamicCrawler` to populate
    :class:`~contracts.models.Tender` table.

    Overwrites :meth:`~DynamicCrawler.clean_data` to clean data to
    :class:`~contracts.models.Tender` and :meth:`~DynamicCrawler.save_instance`
    to also save ``ManytoMany`` relationships of the
    :class:`~contracts.models.Tender`.

    Uses:

    * :attr:`object_directory`: ``'../../data/tenders'``
    * :attr:`object_name`: ``'tender'``;
    * :attr:`object_url`: ``'http://www.base.gov.pt/base2/rest/anuncios/%d'``
    * :attr:`object_model`: :class:`~contracts.models.Tender`.


Crawler for Categories
======================

.. currentmodule:: contracts.categories_crawler

.. _CPVS: http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
.. _tree: https://en.wikipedia.org/wiki/Tree_(data_structure)
.. _`nested set`: https://en.wikipedia.org/wiki/Nested_set_model
.. _`XML file`: https://raw.githubusercontent.com/data-ac-uk/cpv/master/etc/cpv_2008.xml

Europe Union has a categorisation system for public contracts, CPVS_, that
translates a string of 8 digits into a category to be used in public contracts.

More than categories, this system is a tree with broader categories like
"agriculture", and more specific ones like "potatos".

They provide the fixture as an `XML file`_, which we import:

.. function:: build_categories()

    Constructs the category tree of :class:`categories <contracts.models.Category>`.

    Gets the most general categories and saves then, repeating this recursively
    to more specific categories until it reaches the leaves of the tree.

    The categories are retrieved from the internet.
