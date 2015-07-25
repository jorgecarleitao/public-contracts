#!/bin/sh
set -e

if [ $CONFIGURATION = "API" ];
then
# install
pip install -r api_requirements.txt

# script
python -m contracts.tools.example

elif [ $CONFIGURATION = "WEBSITE" ]
then
# install
pip install -r website_requirements.txt

# script
python -m contracts.tools.example
# todo: add test to `python manage.py runserver`

elif [ $CONFIGURATION = "PRODUCTION" ]
then
# install
pip install -r production_requirements.txt

# script
python -m contracts.tools.example
mkdir cached_html
PYTHONPATH=$PYTHONPATH:`pwd` django-admin.py test --settings=main.settings_test law.test contracts.test
fi
