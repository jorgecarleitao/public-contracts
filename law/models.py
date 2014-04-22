# coding=utf-8
import re
from BeautifulSoup import BeautifulSoup, Tag

from django.core.urlresolvers import reverse
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

    def get_base_url(self):
        return dre_url_formater.format(document_id=self.dre_doc_id)

    def get_pdf_url(self):
        return "http://dre.pt/%s" % self.pdf_url

    def get_absolute_url(self):
        return reverse('law_view', args=[self.pk])

    def compose_summary(self):
        soup = BeautifulSoup(self.summary)

        for element in soup.findAll('a'):
            try:
                dre_doc_id = int(element['href'].split('=')[1])
                document = Document.objects.get(dre_doc_id=dre_doc_id)
            except:
                ## other link
                continue
            element['href'] = document.get_absolute_url()
        return soup

    def _compose_text(self):
        self.text = ' '.join(self.text.split())

        ## to substitute <br> by </p><p>
        self.text = self.text.replace("<br />", "</p><p>")
        self.text = unicode(self.text)

        # create <p>'s specifically for start of articles
        self.text = re.sub(u"<p> Artigo (\d+)\.º (.*)</p>",
                           lambda m: u"<p>Artigo %s.º</p><p>%s</p>" % m.group(1, 2),
                           self.text)

        ## to create references
        types = list(Type.objects.exclude(name__contains='('))

        def create_regex():
            regex = u'('
            for name in [type.name for type in types]:
                regex += name + u'|'
            regex = regex[:-1]
            regex += ur') n.º (.*?/\d+)'
            return regex

        def replace_docs(match):
            matched_type_name, matched_number = match.group(1, 2)
            matched_type = next(type for type in types if type.name == matched_type_name)
            matched_number = matched_number.strip()

            default = u'%s n.º %s' % (matched_type_name, matched_number)

            try:
                doc = Document.objects.get(type_id=matched_type.id, number=matched_number)
            except Document.DoesNotExist:
                return default

            return u'<a class="reference-%d" href=%s>%s</a>' % (doc.id, doc.get_absolute_url(),default)

        self.text = re.sub(create_regex(), replace_docs, self.text)

        ## to add blockquote to changes
        self.text = self.text.replace(u'» </p>', u'»</p>')
        self.text = self.text.replace(u'<p> «', u'<p>«')

        self.text = re.sub(u"<p>«(.*?)»</p>",
                           lambda m: u"<blockquote><p>%s</p></blockquote>" % m.group(1),
                           self.text, flags=re.MULTILINE)

        ## general formatting
        def scrape_article_number(element):
            article_number = re.search(u'Artigo (.*)', element.text).group(1)
            return article_number

        soup = BeautifulSoup(self.text)

        soup.find('p').extract()  # name
        soup.find('p').extract()  # date

        previous_element = None
        current_article = None
        current_number = None

        format_headers = {u'CAPÍTULO': 'h3',
                          u'SECÇÃO': 'h4',
                          u'ANEXO': 'h4',
                          u'Artigo': 'h5'}

        for element in soup.findAll('p'):
            # format headers
            for format in format_headers:
                if element.text.startswith(format):
                    element.name = format_headers[format]
                    element['class'] = 'text-center'
                    break

            # format the headers's title
            for format in format_headers:
                if previous_element and previous_element.text.startswith(format):
                    element.name = format_headers[format]
                    element['class'] = 'text-center'
                    break

            if element.text.startswith(u'Artigo'):
                # if not quoting, we define which article we are
                if not element.findParents('blockquote'):
                    current_article = scrape_article_number(element)
                    element['id'] = 'article-%s' % current_article

            search = re.search(r"^(\d+) - ", element.text)
            if search:
                current_number = search.group(1)

            if element.text == u'(ver documento original)':
                anchor = Tag(soup, "a")
                anchor['href'] = self.get_pdf_url()
                anchor.string = u'(ver documento original)'

                element.clear()
                element.append(anchor)

            previous_element = element

        return soup

    def compose_text(self):
        """
        Wrapper to avoid errors, since compose_text is experimental at this point.
        """
        try:
            return self._compose_text()
        except:
            return self.text
