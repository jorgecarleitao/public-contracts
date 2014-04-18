# coding=utf-8
from BeautifulSoup import BeautifulSoup

from django.db import models


# document_id is represented by 8 numbers: year#### (e.g. 19971111)
dre_url_formater = "http://dre.pt/cgi/dr1s.exe?" \
                   "t=d" \
                   "&cap=" \
                   "&doc={document_id}" \
                   "&v01=" \
                   "&v02=" \
                   "&v03=" \
                   "&v04=" \
                   "&v05=" \
                   "&v06=" \
                   "&v07=" \
                   "&v08=" \
                   "&v09=" \
                   "&v10=" \
                   "&v11=" \
                   "&v12=" \
                   "&v13=" \
                   "&v14=" \
                   "&v15=" \
                   "&v16=" \
                   "&v17=" \
                   "&v18=" \
                   "&v19=" \
                   "&v20=" \
                   "&v21=" \
                   "&v22=" \
                   "&v23=" \
                   "&v24=" \
                   "&v25=" \
                   "&sort=0" \
                   "&submit=Pesquisar"


class Type(models.Model):
    name = models.CharField(max_length=254, unique=True)

    def __unicode__(self):
        return self.name


class Creator(models.Model):
    name = models.CharField(max_length=254, unique=True)

    def __unicode__(self):
        return self.name


class Document(models.Model):
    type = models.ForeignKey(Type)
    creator = models.ForeignKey(Creator, null=True)

    date = models.DateField()
    number = models.CharField(max_length=20, null=True)

    dre_doc_id = models.IntegerField(unique=True, db_index=True)

    series = models.IntegerField(db_index=True)
    series_number = models.CharField(max_length=10)
    series_other = models.CharField(max_length=30, blank=True)
    series_pages = models.CharField(max_length=50)

    summary = models.TextField()

    def get_base_url(self):
        return dre_url_formater.format(document_id=self.dre_doc_id)

    def compose_summary(self):
        soup = BeautifulSoup(self.summary)

        for element in soup.findAll('a'):
            try:
                dre_doc_id = int(element['href'].split('=')[1])
            except:
                ## other link
                continue
            element['href'] = dre_url_formater.format(document_id=dre_doc_id)
        return soup
