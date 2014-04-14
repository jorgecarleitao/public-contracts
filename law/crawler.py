# coding=utf-8
import pickle
import re
import urllib2
import datetime

from BeautifulSoup import BeautifulSoup

from django.utils.text import slugify

from contracts.crawler import AbstractCrawler

from models import Type, Document, convert_to_url


class FirstSeriesCrawler(AbstractCrawler):
    """
    A crawler for the Series I of DRE. It goes to all known lists
    and creates a list of ids.

    Next, it parses each list and stores the result in the DB.

    The lists are also file-cached, to avoid hitting DRE.
    """

    class LastPageError:
        pass

    def __init__(self):
        super(FirstSeriesCrawler, self).__init__()

        self.data_directory = '../../law_data'
        self.source_directory = self.data_directory + '/source'

        #type = 'Decreto-Lei', 'Lei', etc.
        self._law_url_formatter = 'http://dre.pt/cgi/dr1s.exe?' \
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
                                  'v11=\'{type}\'&' \
                                  'v12=&' \
                                  'v13=&' \
                                  'v14=&' \
                                  'v15=&' \
                                  'sort=0&' \
                                  'submit=Pesquisar'

        #type = 'Decreto-Lei', 'Lei', etc.
        self._list_url_formatter = 'http://dre.pt/cgi/dr1s.exe?' \
                                   't=qr&' \
                                   'titp=100&' \
                                   'pag={page}&' \
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
                                   'v11=\'{type}\'&' \
                                   'v12=&' \
                                   'v13=&' \
                                   'v14=&' \
                                   'v15=&' \
                                   'sort=0&' \
                                   'submit=Pesquisar'

    @staticmethod
    def get_doc_id(url):
        if "$$N REGISTO" in url:
            return None
        return int(re.findall(r'doc=(\d+)', url)[0])

    def extract_law_types(self):
        """
        Retrieves all types of documents from the list in DR website. Adds others found.
        """
        url = 'http://dre.pt/comum/html/janelas/dip1s_ltipos.html'

        html = self.goToPage(url)
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

        for element in soup.findAll('li'):
            Type.objects.get_or_create(name=element.text)

        # Others meanwhile found
        Type.objects.get_or_create(name=u"Acórdão doutrinário")
        Type.objects.get_or_create(name=u"Acórdão - Recurso extraordinário")
        Type.objects.get_or_create(name=u"Acórdão do Supremo Tribunal de Justiça")
        Type.objects.get_or_create(name=u"Acórdão do Supremo Tribunal Administrativo")
        Type.objects.get_or_create(name=u"Acórdão do Tribunal Constitucional")
        Type.objects.get_or_create(name=u"Acórdão do Tribunal de Contas")
        Type.objects.get_or_create(name=u"Decreto de aprovação da Constituição")
        Type.objects.get_or_create(name=u"Decreto do Representante da República para a Região Autónoma da Madeira")
        Type.objects.get_or_create(name=u"Decreto do Representante da República para a Região Autónoma dos Açores")
        Type.objects.get_or_create(name=u"Resolução da Assembleia Legislativa da Região Autónoma dos Açores")
        Type.objects.get_or_create(name=u"Resolução da Assembleia Legislativa da Região Autónoma da Madeira")
        Type.objects.get_or_create(name=u"Despacho ministerial")
        Type.objects.get_or_create(name=u"Despacho do Conselho de Ministros")
        Type.objects.get_or_create(name=u"Despacho interpretativo")
        Type.objects.get_or_create(name=u"Despacho do Conselho Superior de Defesa Nacional")
        Type.objects.get_or_create(name=u"Despacho conjunto regulamentar")
        Type.objects.get_or_create(name=u"Despacho conjunto")
        Type.objects.get_or_create(name=u"Despacho ministerial conjunto")
        Type.objects.get_or_create(name=u"Orçamento")
        Type.objects.get_or_create(name=u"Orçamento ordinário")
        Type.objects.get_or_create(name=u"Orçamento suplementar")
        Type.objects.get_or_create(name=u"Moção de censura")

    @staticmethod
    def clear_and_save_summary(datum):
        """
        Parses and cleans a given datum obtained from extract_from_list_element.

        Returns a dictionary with
         - 'type': The type of the document, a 'Type'
         - 'number': None or the number of the document, a string.
         - 'dr_doc_id': The document number in the official database, an int.
         - 'dr_series': the series (typically 'I')
         - 'dr_number': the number of the series
         - 'summary': the official summary of the document.
        """

        data = {'number': None}

        strings = datum['data'].replace(u'.DG', u'. DG')
        strings = strings.replace(u'  ', u' ')
        strings = strings.split('. ')

        type_name = strings[0]

        if u'Aviso (1.ª parte)' in type_name or u'Aviso (2.ª parte)' in type_name:
            type_name = u'Aviso'

        if u'n.º' in strings[0]:
            sub_string = strings[0].split(u' n.º ')
            type_name = sub_string[0]
            data['number'] = sub_string[1]

        if type_name == u'(Não especificado)':
            type_name = None
        else:
            search = re.search(u"^(.*) de (\d+) de (.*) de (\d+)", type_name)
            search1 = re.search(u"(\w+) de (\d+) de (.*)", type_name)
            # Changes in Portuguese orthography has its downsides...
            if type_name == u'Declaração de Retificação':
                type_name = u'Declaração de Rectificação'
            if type_name == u'Declarações':
                type_name = u'Declaração'
            elif search:
                type_name = search.group(1)
            elif search1:
                type_name = search1.group(1)

        strings = strings[1].split(u' de ')

        if u"Assembleia da República" in strings[1]:
            strings[1] = strings[1].split(' ')[0]

        data['date'] = datetime.datetime.strptime(strings[1], "%Y-%m-%d").date()

        strings = strings[0].split(u" SÉRIE ")

        data['dr_number'] = strings[0]
        data['dr_series'] = strings[1]

        ## minor typos in the official website
        if type_name == u'Decreto do Presidente de República':
            type_name = u'Decreto do Presidente da República'
        if type_name == u'Resolução de Assembleia Regional':
            type_name = u'Resolução da Assembleia Regional'
        if type_name == u'Resolução de Conselho de Ministros':
            type_name = u'Resolução do Conselho de Ministros'
        if type_name == u'Resolução da  Assembleia da República':
            type_name = u'Resolução da Assembleia da República'
        if type_name in (u'1.º orçamento suplementar',
                         u'1º Orçamento suplementar',
                         u'1.º Orçamento suplementar',
                         u'1.° Orçamento suplementar ',
                         u'2.º Orçamento suplementar',
                         u'2.º orçamento suplementar',
                         u'3.º Orçamento suplementar'):
            type_name = u'Orçamento suplementar'

        if type_name is not None:
            try:
                data['type'] = Type.objects.get(name=type_name)
            except Type.DoesNotExist:
                print "'%s' not found." % type_name
                raise
        else:
            data['type'] = None

        data['dr_doc_id'] = datum['doc_id']

        data['summary'] = datum['summary'].strip()

        return data

    def scrape_summary(self, summary):
        """
        Scrapes a (soup) summary of the list parsed from html.
        Returns a dictionary of non-validated strings.
        """
        entry = {}
        href = summary.find("a", dict(title="Link para o documento da pesquisa."))
        entry['doc_id'] = self.get_doc_id(href['href'])
        entry['data'] = href.text
        entry['entity'] = summary.find("span", {'class': 'bold'}).text
        entry['summary'] = unicode(summary).split('<br />')[-1].replace('</li>', '')

        return entry

    def retrieve_and_scrape_summaries(self, page, type_name):
        """
        Given a page and a type name, returns a list of non-validated summaries.
        """
        print(u"retrieve_and_scrape_summaries(%d, '%s')" % (page, slugify(type_name)))

        html_encoded_type = convert_to_url(type_name)
        html = self.goToPage(self._list_url_formatter.format(page=page, type=html_encoded_type))
        soup = BeautifulSoup(html)

        l = soup.find("div", dict(id="lista"))

        data = []
        for summary in l.findAll("li"):
            data.append(self.scrape_summary(summary))

        return data

    def get_last_page(self, type_name):
        """
        Returns the last parsed page, searching the last cached file.
        """
        import os
        regex = re.compile(r"%s_(\d+).dat" % slugify(type_name))
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s/' % self.data_directory) if re.match(regex, f)]

        files = sorted(files, key=lambda x: int(x), reverse=True)
        if len(files):
            return files[0] - 1
        else:
            return 0

    def get_summaries(self, page, type_name):
        """
         Given a page and type_name, downloads and scrapes the list of
         non-validated summaries in it.

         The result is cached such that there is only one download per (page, type_name).

         - If list is not complete (100 elements), downloads it again and re-saves it.
         - If there is only 1 element, we skip it since every list in DRE returns at least one element.
        """
        # fixme: the 1 element condition makes the crawler to skip type names that only have one element.

        file_name = '%s/%s_%d.dat' % (self.data_directory, slugify(type_name), page)
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            if len(data) != 100:  # if page is not complete, we retrieve it again to try to complete it.
                print '_get_summaries(%d)' % page,
                print 'returns len(data) = %d != 100' % len(data)
                raise IOError
            f.close()
        except IOError:
            # online retrieval
            data = self.retrieve_and_scrape_summaries(page, type_name)

            if len(data) == 1:  # if 1 entry, it means it is a repeated entry and we stop
                raise self.LastPageError

            f = open(file_name, "wb")
            pickle.dump(data, f)
            f.close()
        return data

    def update_all(self):
        """
        Entry point of this crawler. For all known types, retrieves, scrapes, clears, and saves
        new documents.
        """
        for type in Type.objects.all():
            print(u'save_all_summaries: saving \'%s\', %d' % (slugify(type), type.id))
            page = self.get_last_page(type.name)
            while True:
                page += 1
                try:
                    summaries = self.get_summaries(page, type.name)
                except self.LastPageError:
                    break
                except urllib2.URLError:
                    break

                for datum in summaries:
                    data = self.clear_and_save_summary(datum)

                    try:
                        Document.objects.get(type=data['type'], dr_doc_id=data['dr_doc_id'])
                    except Document.DoesNotExist:
                        print("New '%s' added" % data['type'])
                        document = Document(**data)
                        document.save()

    def retrieve_text_source(self, doc_id, type_name):
        """
        Retrieves the source of the document.
        """
        print("get_source(%d)" % doc_id)
        file_name = '%s/source/%d_%s.dat' % (self.data_directory, doc_id, slugify(type_name))
        try:
            f = open(file_name, "rb")
            html = pickle.load(f)
            f.close()
        except IOError:
            # online retrieval

            html_encoded_type = convert_to_url(type_name)
            html = self.goToPage(self._law_url_formatter.format(doc_id=doc_id, type=html_encoded_type))

            soup = BeautifulSoup(html)

            html = unicode(soup.find("div", dict(id='centro_total')))

            f = open(file_name, "wb")
            pickle.dump(html, f)
            f.close()
        return html

    def retrieve_all_text_sources(self):
        """
        Not being used.
        """
        for type in Type.objects.all():
            print(u'save_all_summaries: saving \'%s\', %d' % (slugify(type), type.id))
            page = 0
            while True:
                page += 1
                try:
                    summaries = self.get_summaries(page, type.name)
                except self.LastPageError:
                    break

                for summary in summaries:
                    try:
                        self.retrieve_text_source(summary['doc_id'], type.name)
                    except IndexError:
                        print(u"fail to parse summary of doc_id=%s" % summary['doc_id'])


class NewFirstSeriesCrawler(AbstractCrawler):

    data_directory = '../../law_data'

    # document_id is represented by 8 numbers: year#### (e.g. 19971111)
    _law_url_formatter = "http://dre.pt/cgi/dr1s.exe?" \
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

    class DocumentNotFound(Exception):
        pass

    def __init__(self):
        super(NewFirstSeriesCrawler, self).__init__()

    def retrieve_document(self, document_id):
        """
        Retrieves the source of the document.
        """
        file_name = '%s/%s.dat' % (self.data_directory, document_id)
        try:
            f = open(file_name, "rb")
            html = pickle.load(f)
            f.close()
        except IOError:
            # online retrieval
            html = self.goToPage(self._law_url_formatter.format(document_id=document_id))

            soup = BeautifulSoup(html)

            html = soup.find("div", dict(id='centro_total'))

            if not html.find('div', {'id': 'doc_data'}):
                raise self.DocumentNotFound

            print(u"saving document_id %d" % document_id)
            f = open(file_name, "wb")
            pickle.dump(html, f)
            f.close()
        return html

    def get_documents(self, year):
        print(u"get_documents(%d)" % year)

        document_number = 1
        fails = 0
        while True:
            try:
                self.retrieve_document(int("%04d%04d" % (year, document_number)))
                fails = 0
            except self.DocumentNotFound:
                fails += 1
                print("DocumentNotFound: %d" % fails)

            if fails == 10:
                break

            document_number += 1

    def retrieve_all(self):
        first_year = 1910
        last_year = datetime.datetime.now().date().year

        for year in xrange(first_year, last_year + 1):
            self.get_documents(year)
