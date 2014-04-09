# coding=utf-8
from django.db import models


def convert_to_url(string):
    """
    Converts unicode chars to some exquisite encoding defined in w3school,
    which the dre uses.
    """
    string = string.replace(u'ã', '%E3')
    string = string.replace(u'á', '%E1')
    string = string.replace(u'â', '%E2')

    string = string.replace(u'ç', '%E7')
    string = string.replace(u'ó', '%F3')
    string = string.replace(u'ê', '%EA')
    string = string.replace(u'õ', '%F5')

    string = string.replace(u'ú', '%FA')
    return string



class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class Document(models.Model):
    type = models.ForeignKey(Type, null=True)
    date = models.DateField()
    number = models.CharField(max_length=20, null=True)

    dr_doc_id = models.IntegerField(null=True)  # some don't have link... yet, they still are Laws...
    dr_number = models.CharField(max_length=20)
    dr_series = models.CharField(max_length=20)  # "I" or "II"

    summary = models.TextField()

    def get_base_url(self):
        if self.type is None:
            return ""

        return 'http://dre.pt/cgi/dr1s.exe?' \
               't=dr&' \
               'cap=1-1200&' \
               'doc={doc_id}&' \
               'v02=&' \
               'v01=2&' \
               'v03=1900-01-01&' \
               'v04=3000-12-21&' \
               'v05=&' \
               'v06=&' \
               'v07=&' \
               'v08=&' \
               'v09=&' \
               'v10=&' \
               'v11={type}&' \
               'v12=&' \
               'v13=&' \
               'v14=&' \
               'v15=&' \
               'sort=0&' \
               'submit=Pesquisar'.format(doc_id=self.dr_doc_id, type=convert_to_url(self.type.name))


# class LawArticle(models.Model):
#     decree = models.ForeignKey(Document)
#
#     number = models.IntegerField()
#     title = models.TextField()
#
#
# class LawText(models.Model):
#     decree = models.ForeignKey(Document, null=True)
#     article = models.ForeignKey(LawArticle, null=True)
#
#     type = models.CharField(max_length=20)
#     number = models.CharField(max_length=5, null=True)
#     index = models.IntegerField()
#
#     text = models.TextField()
