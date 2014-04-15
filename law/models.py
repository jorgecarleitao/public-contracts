# coding=utf-8
from BeautifulSoup import BeautifulSoup

from django.db import models


class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class Document(models.Model):
    type = models.ForeignKey(Type, null=True)
    date = models.DateField()
    number = models.CharField(max_length=20, null=True)

    dr_doc_id = models.IntegerField(unique=True, db_index=True)

    summary = models.TextField()

    def get_base_url(self):
        return "http://dre.pt/cgi/dr1s.exe?" \
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
                         "&submit=Pesquisar".format(document_id=self.dr_doc_id)

    def compose_summary(self):

        soup = BeautifulSoup(self.summary)

        for element in soup.findAll('a'):
            try:
                doc_id = int(element['href'].split('=')[1])
            except:
                continue
            document = Document.objects.get(dr_doc_id=doc_id)
            element['href'] = document.get_base_url()
        return soup
