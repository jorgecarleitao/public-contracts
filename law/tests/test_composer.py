import unittest
from datetime import datetime
import re

from law.composer import get_documents
from law.models import Document, Type


class ComposerTestCase(unittest.TestCase):

    def test_multi_documents_references(self):

        type = Type.objects.create(name='Decreto-Lei')
        Document.objects.create(type=type, date=datetime.now(),
                                dre_doc_id=1, dr_series='I',
                                number='64/2006',
                                dre_pdf_id=1)
        Document.objects.create(type=type, date=datetime.now(),
                                dre_doc_id=2, dr_series='I',
                                number='88/2006',
                                dre_pdf_id=2)
        Document.objects.create(type=type, date=datetime.now(),
                                dre_doc_id=3, dr_series='I',
                                number='196/2006',
                                dre_pdf_id=3)
        Document.objects.create(type=type, date=datetime.now(),
                                dre_doc_id=4, dr_series='I',
                                number='393-B/99',
                                dre_pdf_id=4)

        # retrieved from doc 317374
        text = "<p>Simultaneamente, e para além de uma simplificação e " \
               "atualização das  disposições do Decreto-Lei n.º 393-B/99, " \
               "de 2 de outubro, alterado pelos  Decretos-Leis n.os 64/2006, " \
               "de 21 de março, 88/2006, de 23 de maio, e  196/2006, " \
               "de 10 de outubro, procede-se, através do presente diploma, " \
               "a um  conjunto de alterações das regras relacionadas com a " \
               "fixação das vagas dos  concursos especiais e com a utilização " \
               "das vagas sobrantes.</p>"

        types = list(Type.objects.exclude(name__contains='('))
        self.assertEqual(get_documents(text, types).count(), 4)
