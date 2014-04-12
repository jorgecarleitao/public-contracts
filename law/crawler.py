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
            print(u'save_all_summaries: saving \'%s\', %d' % (type, type.id))
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

    def get_source(self, doc_id):
        """
        Not being used.
        """
        print("get_source(%d)" % doc_id)
        file_name = '%s/source/%d.dat' % (self.data_directory, doc_id)
        try:
            f = open(file_name, "rb")
            html = pickle.load(f)
            f.close()
        except IOError:
            # online retrieval
            html = self.goToPage(self._law_url_formatter.format(doc_id=doc_id))

            f = open(file_name, "wb")
            pickle.dump(html, f)
            f.close()
        return html

    def get_all_sources(self):
        """
        Not being used.
        """
        page = 0
        while True:
            try:
                entries = self.get_summaries(page)
            except self.LastPageError:
                break

            for entry in entries:
                try:
                    self.get_source(self.get_doc_id(entry['href']))
                except IndexError:
                    print("fail to parse entry with url %s" % entry['href'])

            page += 1

    def get_law_url(self, doc_id):
        return self._law_url_formatter.format(doc_id=doc_id)

    def parse_source_data(self, doc_id):
        """
        Not being used.
        """
        print('parse_source_data(%d)' % doc_id)

        data = {'dr_doc_id': doc_id}

        html = self.get_source(doc_id)
        soup = BeautifulSoup(html)

        data_element = soup.find('div', {'id': 'doc_data'})

        for element in data_element.findAll('p'):
            if u"DATA" in element.text:
                data['date'] = clean_date(element.text)
                continue
            if u'NÚMERO' in element.text:
                data['dr_number'], data['dr_series'] = clean_series(element.text)
                continue
            if u"DIPLOMA / ATO" in element.text:
                data['type'], data['number'] = clean_type(element.text)
                continue
            if u"PÁGINAS" in element.text:
                search = re.search('([0-9\(-\)]+) a ([0-9\(-\)]+)', element.text)
                data['pages'] = u"[%s, %s]" % (search.group(1), search.group(2))
                continue

        return data

    def parse_source_text(self, doc_id):
        """
        Not being used.
        """
        decree = Document.objects.get(dr_doc_id=doc_id)

        html = self.get_source(doc_id)
        soup = BeautifulSoup(html)

        text_element = soup.find('div', {'id': 'doc_texto'})

        state = {'quote': False}

        previously_created = None
        current_article = None

        index = 0
        for element in text_element.findAll('p'):
            text = element.text

            if u'TEXTO' in text:
                continue

            index += 1

            # 'quote' implies the text is being parsed as a change in other text.
            if text[0] == u'«':
                state['quote'] = True
                text = text[1:]
            elif text[-1] == u'»':
                state['quote'] = False
                text = text[:1]
                continue

            if state['quote']:
                previously_created, created = LawText.objects.get_or_create(type='quote',
                                                                            text=text,
                                                                            article=current_article,
                                                                            decree=decree,
                                                                            index=index)
                continue

            # identify articles
            search_article = re.search('^Artigo (\d+).\xba$', text)
            if search_article:
                previously_created, created = LawArticle.objects.get_or_create(decree=decree,
                                                                               number=int(search_article.group(1)))
                current_article = previously_created
                continue

            if previously_created is not None and isinstance(previously_created, LawArticle):
                previously_created.title = text
                previously_created.save()
                previously_created = None
                continue

            search_numeral_bullet = re.search('^(\d+) - (.*)', text)
            if search_numeral_bullet:
                previously_created, created = LawText.objects.get_or_create(type='numeral',
                                                                            text=search_numeral_bullet.group(2),
                                                                            article=current_article,
                                                                            decree=decree,
                                                                            number=int(search_numeral_bullet.group(1)),
                                                                            index=index)

                continue

            search_alphabetic_bullet = re.search('^(\w)\) (.*)', text)
            if search_alphabetic_bullet:
                previously_created, created = LawText.objects.get_or_create(type='alphabetic',
                                                                            text=search_alphabetic_bullet.group(2),
                                                                            article=current_article,
                                                                            decree=decree,
                                                                            number=search_alphabetic_bullet.group(1),
                                                                            index=index)
                continue


            previously_created, created = LawText.objects.get_or_create(type='other',
                                                                        text=text,
                                                                        article=current_article,
                                                                        decree=decree,
                                                                        index=index)

    def parse_changes(self, doc_id):
        """
        Not being used.
        """
        decree = LawDecree.objects.get(dr_doc_id=doc_id)

        for article in decree.lawarticle_set.all():
            entries = LawText.objects.filter(article=article)
            print(u"Article nº %d" % article.number)

            ## we see if this article changes any decree
            search = re.search(u'n.º (.*),', article.title)
            if u'Alteração' in article.title and search:
                changing_decree = LawDecree.objects.get(number=search.group(1))
            else:
                continue

            ## we now start constructing the changes
            changing_article = None
            for entry in entries:
                print entry.text

                search = re.search('^Artigo (\d+).\xba$', entry.text)
                if search and changing_article is None:
                    changing_article = LawArticle.objects.get(number=search.group(1), decree=changing_decree)

                if changing_article is None:
                    continue

    def parse_all(self):
        """
        Not being used.
        """
        page = 1
        while True:
            try:
                entries = self.get_summaries(page)
            except self.LastPageError:
                break

            for entry in entries:
                try:
                    doc_id = self.get_doc_id(entry['href'])
                except IndexError:
                    continue

                self.parse_source_text(doc_id)
            page += 1

    def save_data(self):
        """
        Not being used.
        """
        page = 1
        while True:
            try:
                entries = self.get_summaries(page)
            except self.LastPageError:
                break

            for entry in entries:
                try:
                    doc_id = self.get_doc_id(entry['href'])
                except IndexError:
                    continue

                data = self.parse_source_data(doc_id)

                try:
                    LawDecree.objects.get(dr_doc_id=doc_id)
                except LawDecree.DoesNotExist:
                    decree = LawDecree(**data)
                    decree.save()
            page += 1
