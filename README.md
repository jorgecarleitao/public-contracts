# Public contracts

Public contracts is an open source Django website and API to analyse and visualise the database of (portuguese) public contracts.
Thanks for checking it out.

## Motivation

Every public entity in European Union has to publicly disclose its
contracts in an [official website](http://simap.europa.eu/supplier/national-procurement-databases/index_en.htm).

The [portuguese database](http://www.base.gov.pt/base2/), with about 400.000 contracts,
spamms orders of magnitude between their prices.

We have a crawler that daily retrieves information from the official database to a database we host,
and we provide read access to anyone. This way, anyone can query it using mysql.

Our [website](http://contratos.publicos.pt) hosts a website (whose code is in this repository)
with analysis of the database.

## The code

We use [Django](https://www.djangoproject.com/) ORM for the API and database
and JQuery and d3.js for visualisations of statistical quantities of the database.
The official website is translated to portuguese (via i18n), also hosted here.

The code is licenced under BSD.

## Documentation

The API and the crawler are [documented](http://public-contracts.readthedocs.org/en/latest/).
This documentation is serious. If you find any mistake, please don't hesitate in filling an issue on github.

## Pre-requisites and installation

1- Install Django and bindings to mysql.

`pip install django`

`pip install mysql-python` 

2- Install [django-treebeard](https://github.com/tabo/django-treebeard), a dependency.

`pip install django-treebeard`

3- Download the source

`git clone git@github.com:jorgecarleitao/public-contracts.git`

Enter in the directory `cd public-contracts/contracts`.

4- Run the example:

`python -m tools.example`

If something went wrong, please drop by our [mailing-list](https://groups.google.com/forum/#!forum/public-contracts)
so we can help you, or report an [issue](https://github.com/jorgecarleitao/public-contracts/issues)
so we can improve these instructions.
