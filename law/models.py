# coding=utf-8
import re
from BeautifulSoup import BeautifulSoup, Tag

from django.core.urlresolvers import reverse
from django.db import models

import composer


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
        ## normalize all text
        text = composer.normalize(self.text)

        ## create references to other documents
        text = composer.add_references(text)

        ## general formatting and items identification
        def scrape_article_number(element):
            article_number = re.search(u'Artigo (.*)\.º', element.text).group(1)
            return article_number

        soup = BeautifulSoup(text)

        soup.find('p').extract()  # name
        soup.find('p').extract()  # date

        previous_element = None

        current_article = None

        current_number = None
        current_number_list = None
        current_number_list_element = None

        blockquote_state = False

        annex_prefix = u''
        article_prefix = u''

        format_headers = {u'Capítulo': 'h3',
                          u'Secção': 'h4',
                          u'Anexo': 'h4',
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

            if element.findParents('blockquote'):
                blockquote_state = True
            if blockquote_state and not element.findParents('blockquote'):
                blockquote_state = False

            # identify articles
            if element.text.startswith(u'Artigo'):
                # if not quoting, we define which article we are
                if not blockquote_state:
                    current_article = scrape_article_number(element)

                    article_prefix = u'artigo-%s' % current_article
                    if annex_prefix:
                        article_prefix = annex_prefix + u'-' + article_prefix
                    element['id'] = article_prefix
            elif element.text.startswith(u'Anexo'):
                current_article = None
                annex_prefix = u'anexo'
                element['id'] = annex_prefix

            # identify numbers
            number_search = re.search(r"^(\d+) - ", element.text)
            if number_search and not blockquote_state:
                current_number = int(number_search.group(1))

            if current_number == 1 and current_number_list is None:
                current_number_list = Tag(soup, 'ol')
                element.replaceWith(current_number_list)

            if not blockquote_state:
                for format in format_headers:
                    ## if a new element starts, the numbering is re-set.
                    if element.text.startswith(format):
                        current_number = None
                        current_number_list = None
                        current_number_list_element = None
                        break

            if current_number is not None:
                if blockquote_state:
                    blockquote_number_list_element = current_number_list_element.find('blockquote')

                    # if there isn't a blockquote, we add it
                    if not blockquote_number_list_element:
                        blockquote_number_list_element = Tag(soup, 'blockquote')
                        current_number_list_element.append(blockquote_number_list_element)

                    blockquote_number_list_element.append(element)
                # there is a new number, we create a new <li>
                elif number_search:
                    print('created new item')
                    number_prefix = u'numero-%d' % current_number
                    if article_prefix:
                        number_prefix = article_prefix + u'-' + number_prefix

                    current_number_list_element = Tag(soup, 'li', {'id': number_prefix})
                    current_number_list.append(current_number_list_element)
                    current_number_list_element.append(element)
                else:
                    current_number_list_element.append(element)

            # add anchors to link statements
            if element.text == u'(ver documento original)':
                anchor = Tag(soup, "a")
                anchor['href'] = self.get_pdf_url()
                anchor.string = u'(ver documento original)'

                element.clear()
                element.append(anchor)

            previous_element = element

        text = unicode(soup)
        return text

    def compose_text(self):
        """
        Wrapper to avoid errors, since compose_text is experimental at this point.
        """
        import traceback
        try:
            return self._compose_text()
        except Exception, e:
            print str(e)
            print traceback.format_exc()
            return composer.normalize(self.text)
