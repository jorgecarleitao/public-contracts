# Public contracts

Public contracts is an open source website to analyse and visualise portuguese public contracts.
The objective of this repository is to host a community that collaborates on the creation of the website.

## Motivation

Every portuguese public entity has to publicly disclose its contracts in an official website,
[Base](http://www.base.gov.pt/base2/). In particular, it has to disclose:

1. to whom the contract was made.
2. how much the contract was.
3. when the contract was made.
4. which [category](http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm) it belongs to.

Currently, this database has about 370.000 contracts, spamming orders of magnitude between their prices.

## The objective
This repository hosts a community interested in contributing to the source of an website
that helps visualising and analysing the database.

We have a crawler that daily retrieves information from Base to a database we host, and we provide read access to the it.
With this access, anyone can fork this code and play with it in the full database. We also provide dumps of the database
to ease the load to our servers and allow offline coding.

This project has an official website that hosts the database and the website created in this collaborative project.

## The code

We use [Django](https://www.djangoproject.com/), JQuery, HTML and CSS, and we write the code in english.
The official website is translated to portuguese to be accessible to anyone in Portugal.

This project is starting, so we still don't have documentation for the collaborative process.
This is our current top priority.

The code is licenced under GPLv2.

## Pre-requisites and installation

1. Get [virtualenv](http://www.virtualenv.org/en/latest/), a must-tool for Python.

`sudo pip install virtualenv`

2. Create a new virtual environment for this project

`virtualenv ~/.env/public-contracts`

(the path `~/.env/public-contracts` can be anything, I use that one).

3. Enter in the virtual environment

`source ~/.env/public-contracts/bin/activate`

4. Install dependencies in the virtual environment

`pip install django`
`pip install python-memcached` <- for caching
`pip install django-treebeard` <- for hierarquical trees in the categories
`pip install mysql-python` <- for using mysql database

5. Install git if required (depends on your operating system)

6. Get the code

go to the directory where you want the code to live and do
`git clone git@github.com:jorgecarleitao/public-contracts.git`
Then, do `cd public-contracts`

7. Start the server

`python manage.py runserver`

8. In your browser, enter in the url `127.0.0.1:80000`.

If something went wrong, please add an issue [here](https://github.com/jorgecarleitao/public-contracts/issues)
so we can help you, and improve this instructions.
