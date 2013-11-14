# Public contracts

Public contracts is an open source Django website and API to analyse and visualise (portuguese) public contracts.
This repository hosts the source code of both the API and the website.

## Motivation

Every public entity in european union has to publicly disclose its contracts in an [official website](http://simap.europa.eu/supplier/national-procurement-databases/index_en.htm). In portuguese case, our first experiment, they disclose:

1. to whom the contract was made.
2. how much the contract was.
3. when the contract was made.
4. which [category](http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm) it belongs to.

Currently, this database has about 370.000 contracts, spamming orders of magnitude between their prices.

We have a (not shared) crawler that daily retrieves information from the official database to a database we host, and we provide read access to the it. This way, we can query it.
This repository shares the API for querying it. In a near future, we will provide dumps of the database
to allow offline querying.

Our [official website](http://contratos.publicos.pt) hosts the website whose code is in this repository (except some
parts relative to the hosting).

## The code

We use [Django](https://www.djangoproject.com/) ORM for the API and database. We use JQuery and d3.js for visualisations of statistical quantities of the database.
The official website is translated to portuguese (via i18n), also hosted here.

The code is licenced under BSD.

## Documentation

The API for accessing the database is fully documented, the website, not yet.

## Pre-requisites and installation

1- Install Django and bindings to mysql.

`pip install django`

`pip install mysql-python` 

2- Install [django-treebeard](https://github.com/tabo/django-treebeard), a dependency.

`pip install django-treebeard`

3- Download the source

`git clone git@github.com:jorgecarleitao/public-contracts.git`

Enter in the directory `cd public-contracts`.

4- Run the example:

`python example.py`

If something went wrong, please drop by our [mailing-list](https://groups.google.com/forum/#!forum/public-contracts) so we can help you, or report an [issue](https://github.com/jorgecarleitao/public-contracts/issues)
so we can improve these instructions.

