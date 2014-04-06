from django.db import models


class LawDecree(models.Model):
    type = models.CharField(max_length=50, null=True)
    date = models.DateField()
    number = models.CharField(max_length=20, null=True)

    dr_doc_id = models.IntegerField(unique=True)
    dr_number = models.CharField(max_length=20)
    dr_series = models.CharField(max_length=20)
    pages = models.CharField(max_length=50)

    text = models.TextField()

    def get_base_url(self):
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
               'v11=\'Decreto-Lei\'&' \
               'v12=&' \
               'v13=&' \
               'v14=&' \
               'v15=&' \
               'sort=0&' \
               'submit=Pesquisar'.format(doc_id=self.dr_doc_id)


class LawArticle(models.Model):
    decree = models.ForeignKey(LawDecree)

    number = models.IntegerField()
    title = models.TextField()


class LawText(models.Model):
    decree = models.ForeignKey(LawDecree, null=True)
    article = models.ForeignKey(LawArticle, null=True)

    type = models.CharField(max_length=20)
    number = models.CharField(max_length=5, null=True)
    index = models.IntegerField()

    text = models.TextField()
