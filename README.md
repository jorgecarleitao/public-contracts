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
