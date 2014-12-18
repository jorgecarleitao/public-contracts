import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify

from .composer import compose_text, compose_summary, normalize


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

    def get_absolute_url(self):
        name = "%s" % slugify(self.name)
        return reverse('law_type', args=[self.pk, name])

    def __unicode__(self):
        return self.name


class Creator(models.Model):
    name = models.CharField(max_length=254, unique=True)

    def __unicode__(self):
        return self.name


class LawDocumentManager(models.Manager):
    """
    A Document manager that only returns laws,
    excluding Diary summaries and technical sheets.
    """
    def get_queryset(self):
        return super(LawDocumentManager, self).get_queryset().exclude(type__id__in=[95, 97, 145, 150])


class Document(models.Model):
    type = models.ForeignKey(Type)
    creator = models.ForeignKey(Creator, null=True)

    date = models.DateField()
    number = models.CharField(max_length=20, null=True)

    summary = models.TextField()

    text = models.TextField(null=True)

    # Where it can be found in the internet (DRE)
    dre_doc_id = models.IntegerField(unique=True, db_index=True)
    pdf_url = models.CharField(max_length=200)

    # Where it can be found in the official book (DR)
    series = models.IntegerField(db_index=True)
    series_number = models.CharField(max_length=10)
    series_other = models.CharField(max_length=30, blank=True)
    series_pages = models.CharField(max_length=50)

    objects = models.Manager()  # default manager.
    laws = LawDocumentManager()

    def get_base_url(self):
        return dre_url_formater.format(document_id=self.dre_doc_id)

    def get_pdf_url(self):
        return "http://dre.pt%s" % self.pdf_url.replace("\\", "/")

    def get_absolute_url(self):
        name = "%s" % slugify(self.type.name)
        if self.number:
            name += '-%s' % self.number
        else:
            name += '-de-' + self.date.strftime('%d/%m/%Y')
        return reverse('law_view', args=[self.pk, name])

    def compose_summary(self):
        return compose_summary(self.summary)

    def compose_text(self):
        """
        Wrapper to avoid errors, since compose_text is experimental at this point.
        """
        if self.text is None:
            return None

        try:
            return compose_text(self)
        except Exception as e:
            logger.exception("Compose text failed in document %d", self.id)
            return normalize(self.text)

    def name(self):
        name = self.type.name

        if self.number:
            name = name + ' ' + self.number
        return name
