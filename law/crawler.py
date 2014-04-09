# coding=utf-8
import pickle
import re
import urllib2
import mechanize as mc
import datetime

from BeautifulSoup import BeautifulSoup

from django.utils.text import slugify

from models import Type, Document, convert_to_url


month_name_to_number = {u'Janeiro': 1,
                        u'Fevereiro': 2,
                        u'Março': 3,
                        u'Abril': 4,
                        u'Maio': 5,
                        u'Junho': 6,
                        u'Julho': 7,
                        u'Agosto': 8,
                        u'Setembro': 9,
                        u'Outubro': 10,
                        u'Novembro': 11,
                        u'Dezembro': 12}


def clean_date(date_string):
    """
    Assumes date of the form
    "Quinta-feira, 17 de Novembro de 2011"

    or

    "17 de Novembro de 2011"
    """
    if ',' in date_string:
        date_string = date_string.split(', ')[1]

    search_date = re.search(u'(\d+) de (\w+) de (\d+)', date_string, re.UNICODE)

    return datetime.date(day=int(search_date.group(1)),
                         month=month_name_to_number[search_date.group(2).title()],
                         year=int(search_date.group(3)))


def clean_series(series_string):
    """
    Assumes string of the form

    "NÚMERO :245/55 SÉRIE I"
    or
    "NÚMERO :250-A SÉRIE I"

    returns ("245/55", "I")
    or
    returns ("250-A", "I")
    """
    search = re.search(u'([0-9/]+) SÉRIE (\w+)', series_string)

    if not search:
        search = re.search(u'([0-9/]+-\w+) SÉRIE (\w+)', series_string)
        return search.group(1), search.group(2)

    return search.group(1), search.group(2)


def clean_type(string):
    if u'(Não especificado)' in string:
        return None, None

    if u'Rectificação' in string:
        return u'Rectificação', None

    if u'Declaração' in string:
        return u'Declaração', None

    if u'Aviso' in string:
        return u'Aviso', None

    parts = string.split(u'n.º ')
    doc_type = parts[0].split(':')[1]
    doc_number = parts[1].split(' ')[0]
    return doc_type, doc_number


class AbstractCrawler(object):

    class NoMoreEntriesError:
        pass

    def __init__(self):
        # Browser
        br = mc.Browser()

        br.set_handle_robots(False)

        # User-Agent. For choosing one, use for instance this with your browser: http://whatsmyuseragent.com/
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) '
                                        'AppleWebKit/537.36 (KHTML, like Gecko)'),
                         ('Range', "items=0-24")]
        self.browser = br

    def goToPage(self, url):
        response = self.browser.open(url)
        return response.read()


class FirstSeriesCrawler(AbstractCrawler):

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

    def extract_law_types(self):
        """
        Retrieves all types of documents and adds others found.
        Valid for series 1 only
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

    def parse_summary_datum(self, datum):

        data = {'number': None}

        strings = datum['data'].replace(u'.DG', u'. DG')
        strings = strings.replace(u'  ', u' ')
        strings = strings.split('. ')

        print strings

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

        if type_name is not None:
            try:
                data['type'] = Type.objects.get(name=type_name)
            except Type.DoesNotExist:
                print type_name, "not found."
                raise
        else:
            data['type'] = None

        data['dr_doc_id'] = datum['doc_id']

        data['summary'] = datum['summary'].strip()

        print data['date']
        return data

    def extract_from_list_element(self, element):
        entry = {}
        href = element.find("a", dict(title="Link para o documento da pesquisa."))
        entry['doc_id'] = self.get_doc_id(href['href'])
        entry['data'] = href.text
        entry['entity'] = element.find("span", {'class': 'bold'}).text
        entry['summary'] = unicode(element).split('<br />')[-1].replace('</li>', '')

        return entry

    def retrieve_and_extract_summaries(self, page, type):
        html_encoded_type = convert_to_url(type)
        html = self.goToPage(self._list_url_formatter.format(page=page, type=html_encoded_type))
        soup = BeautifulSoup(html)

        l = soup.find("div", dict(id="lista"))

        data = []
        for element in l.findAll("li"):
            data.append(self.extract_from_list_element(element))

        return data

    def get_summaries(self, page, type):
        print("get_summaries(%d, '%s')" % (page, type))
        file_name = '%s/%s_%d.dat' % (self.data_directory, slugify(type), page)
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
            data = self.retrieve_and_extract_summaries(page, type)

            if len(data) == 1:  # if 1 entry, it means it is a repeated entry and we stop
                raise self.LastPageError

            f = open(file_name, "wb")
            pickle.dump(data, f)
            f.close()
        return data

    def retrieve_all_summaries(self):
        for type in Type.objects.all():
            print(u'retrieve_all_summaries: retrieving \'%s\'' % type)
            page = 0
            while True:
                page += 1
                try:
                    self.get_summaries(page, type.name)
                except self.LastPageError:
                    break
                except urllib2.URLError:
                    print('error')
                    break

    def save_all_summaries(self):
        for type in Type.objects.all():
            print(u'save_all_summaries: saving \'%s\'' % type)
            page = 0
            while True:
                page += 1
                try:
                    summaries = self.get_summaries(page, type.name)
                except self.LastPageError:
                    break
                except urllib2.URLError:
                    break

                for datum in summaries:
                    data = self.parse_summary_datum(datum)

                    try:
                        Document.objects.get(type=data['type'], dr_doc_id=data['dr_doc_id'])
                    except Document.DoesNotExist:
                        document = Document(**data)
                        document.save()

    def get_source(self, doc_id):
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
        page = 300
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

    def get_doc_id(self, url):
        if "$$N REGISTO" in url:
            return None
        return int(re.findall(r'doc=(\d+)', url)[0])

    def parse_source_data(self, doc_id):
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
