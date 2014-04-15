# coding=utf-8
import pickle
import datetime

from BeautifulSoup import BeautifulSoup
from contracts.crawler import AbstractCrawler

from models import Type


class FirstSeriesCrawler(AbstractCrawler):

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
        super(FirstSeriesCrawler, self).__init__()

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
