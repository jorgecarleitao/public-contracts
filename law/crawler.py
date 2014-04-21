# coding=utf-8
import datetime
import re
import os

from BeautifulSoup import BeautifulSoup
from contracts.crawler import AbstractCrawler

from models import Type, Creator, Document
import models


class FirstSeriesCrawler(AbstractCrawler):

    data_directory = '../../law_data'

    # document_id is represented by 8 numbers: year#### (e.g. 19971111)

    class DocumentNotFound(Exception):
        pass

    def __init__(self):
        super(FirstSeriesCrawler, self).__init__()

    def retrieve_document(self, document_id):
        """
        Retrieves the source of the document.
        """
        file_name = '%s/%s.dat' % (self.data_directory, document_id)
        try:
            f = open(file_name, "rb")
            try:
                html = f.read()
            finally:
                f.close()
        except IOError:
            # online retrieval
            html = self.goToPage(models.dre_url_formater.format(document_id=document_id))

            soup = BeautifulSoup(html)

            html = soup.find("div", dict(id='centro_total'))

            if not html.find('div', {'id': 'doc_data'}):
                raise self.DocumentNotFound

            print(u"saving document_id %d" % document_id)
            f = open(file_name, "wb")
            try:
                f.write(str(html))
            finally:
                f.close()
        return html

    def last_document_id(self, year):
        regex = re.compile(r"%04d(\d+).dat" % year)
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s/' % self.data_directory) if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x), reverse=True)
        if len(files):
            return files[0]
        else:
            return 1

    def get_documents(self, year):
        print(u"get_documents(year=%d)" % year)
        document_number = self.last_document_id(year)
        fails = 0
        while True:
            try:
                self.retrieve_document(int("%04d%04d" % (year, document_number)))
                fails = 0
            except self.DocumentNotFound:
                fails += 1
                print("DocumentNotFound: %d" % fails)

            if fails == 50:
                break

            document_number += 1

    def retrieve_all(self):
        first_year = 1910
        last_year = datetime.datetime.now().date().year

        for year in range(first_year, last_year + 1):
            self.get_documents(year)


def clean_data(data_string):
    soup = BeautifulSoup(data_string)

    doc_data = soup.find('div', {'id': 'doc_data'})

    data = {}
    for element in doc_data.findAll('p'):
        if element.find('span'):
            identifier = element.find('span').extract()
        else:
            continue
        string = ' '.join(element.text.split()).strip()  # remove double white spaces

        if identifier.text.startswith(u'DATA'):
            data['date'] = clean_date(string)
        elif identifier.text.startswith(u'DIPLOMA'):
            data['type'], data['number'] = clean_type_and_number(string)
        elif identifier.text.startswith(u'NÚMERO'):
            data['series'], data['series_number'], data['series_other'] = clean_series(string)
        elif identifier.text.startswith(u'EMISSOR'):
            data['creator'] = clean_creator(string)
        elif identifier.text.startswith(u'PÁGINAS'):
            data['series_pages'] = clean_pages(string)
        elif identifier.text.startswith(u'SUMÁRIO'):
            data['summary'] = clean_summary(element)
        elif element.text == u'':
            pass
        else:
            print [element.text]
            raise IndexError(element.text)

    doc_text = soup.find('div', {'id': 'doc_texto'})
    data['text'] = clean_text(doc_text)

    doc_boxes = soup.find('div', {'id': 'doc_caixas'})
    if doc_boxes is not None:
        doc_pdf = doc_boxes.find('div', {'class': 'cx_pdf'})
        pdf_anchor = doc_pdf.find('a')
        data['pdf_url'] = pdf_anchor['href']

    return data


def clean_date(string):
    if ',' in string:
        string = string.split(u', ')[-1]
    elif string[0] in [str(x) for x in range(1, 9)] or string[0:2] in [str(x) for x in range(10, 30)]:
        pass
    else:
        string = ' '.join(string.split(u' ')[1:])

    if u'Nota:' in string:
        string = string.split(u' Nota:')[0]

    date = datetime.datetime.strptime(string.encode('utf-8'), u'%d de %B de %Y').date()
    return date


def clean_type_and_number(string):
    if u'n.º' in string:
        matches = re.search(u'(.*) n\.º (.*) \(?', string)
        type_name = matches.group(1).strip()
        number = matches.group(2).strip()
    else:
        type_name = string.strip()
        number = None

    # synonymous and typos check
    if type_name == u'Declaração de Retificação':
        type_name = u'Declaração de Reticficação'
    if type_name == u'Decreto do Presidente de República':
        type_name = u'Decreto do Presidente da República'
    if type_name == u'Resolução da  Assembleia da República':
        type_name = u'Resolução da Assembleia da República'

    type, created = Type.objects.get_or_create(name=type_name)

    return type, number


def clean_series(string):
    strings = string.split(u' SÉRIE ')

    series_number = strings[0]
    series_string = strings[1]

    if series_string[0] == 'I':
        series = 1
        series_other = series_string[1:]
    elif series_string[0:1] == 'II':
        series = 2
        series_other = series_string[2:]
    else:
        raise IndexError(series_string)

    return series, series_number, series_other


def clean_creator(string):
    creator_name = string.strip()

    creator, created = Creator.objects.get_or_create(name=creator_name[:254])
    return creator


def clean_pages(string):
    return string


def clean_summary(element):
    search = re.search("<p>(.*)</p>", str(element).strip())
    return search.group(1).strip()


def clean_text(doc_text):
    if 'TEXTO' in str(doc_text.find('p')):
        doc_text.find('p').extract()
    else:
        return None

    text = str(doc_text).strip()
    text = text.replace('<div id="doc_texto">', '')
    text = text.replace('</div>', '')
    return text


class Populator:

    data_directory = '../../law_data'

    def __init__(self):
        import locale
        locale.setlocale(locale.LC_TIME, "pt_pt")
        pass

    class DocumentNotFound(Exception):
        pass

    def get_document(self, document_id):
        file_name = '%s/%d.dat' % (self.data_directory, document_id)

        try:
            f = open(file_name, "r")
            try:
                return f.read()
            finally:
                f.close()
        except IOError:
            raise self.DocumentNotFound

    def populate_from_document(self, document_id, data):
        print("populate_from_document(%d)" % document_id)
        data = clean_data(data)
        data['dre_doc_id'] = document_id

        try:
            document = Document.objects.get(dre_doc_id=document_id)
        except Document.DoesNotExist:
            document = Document()

        for attr, value in data.iteritems():
            setattr(document, attr, value)
        document.save()

        return document

    def get_cached_documents_id_list(self, year):
        regex = re.compile(r"(%04d\w+).dat" % year)
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s/' % self.data_directory) if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x))
        return files

    def populate_documents(self, year):
        for document_id in self.get_cached_documents_id_list(year):
            data = self.get_document(document_id)
            self.populate_from_document(document_id, data)

    def populate_all(self, first_year=1910):
        Type.objects.all().delete()
        last_year = datetime.datetime.now().date().year
        for year in xrange(first_year, last_year + 1):
            self.populate_documents(year)
