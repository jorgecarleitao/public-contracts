# coding=utf-8
from __future__ import unicode_literals

import re
from bs4 import BeautifulSoup, NavigableString

from django.db.models import Q
from django.utils.text import slugify


PLURALS = {'Decreto-Lei': 'Decretos-Leis',
           'Lei': 'Leis',
           'Portaria': 'Portarias'}

SINGULARS = {'Decretos-Leis': 'Decreto-Lei',
             'Leis': 'Lei',
             'Portarias': 'Portaria'}


def normalize(text):

    text = ' '.join(text.split())

    ## to substitute <br/> by </p><p>
    text = text.replace("<br />", "<br/>")
    text = text.replace("<br/>", "</p><p>")
    text = text.replace("<br >", "<br>")
    text = text.replace("<br>", "</p><p>")

    ## strip inside tags
    text = text.replace('<p> ', '<p>')
    text = text.replace(' </p>', '</p>')

    text = text.replace('ARTIGO', 'Artigo')
    text = text.replace('PARTE', 'Parte')
    text = text.replace('TÍTULO', 'Título')
    text = text.replace('CAPÍTULO', 'Capítulo')
    text = text.replace('SECÇÃO', 'Secção')
    text = text.replace('ANEXO', 'Anexo')

    # older documents use "Art." instead of "Artigo"; change it
    text = re.sub('Art\. (\d+)\.º (.*?)',
                  lambda m: "Artigo %s.º %s" % m.group(1, 2),
                  text)

    # older documents use "Artigo #.º - 1 -" instead of "Artigo #.º 1 -"; change it
    text = re.sub('Artigo (\d+)\.º - (.*?)',
                  lambda m: "Artigo %s.º %s" % m.group(1, 2),
                  text)

    # create <p>'s specifically for start of articles
    text = re.sub("<p>Artigo (\d+)\.º (.*?)</p>",
                  lambda m: "<p>Artigo %s.º</p><p>%s</p>" % m.group(1, 2),
                  text)

    ## add blockquote to changes
    text = text.replace('» </p>', '»</p>')
    text = text.replace(r'<p> «', r'<p>«')

    text = re.sub("<p>«(.*?)»</p>",
                  lambda m: "<blockquote><p>%s</p></blockquote>" % m.group(1),
                  text, flags=re.MULTILINE)

    # normalize bullets to "# -" (substituting the ones using #.)
    text = re.sub(r"<p>(\d+)\.",
                  lambda m: "<p>%s -" % m.group(1),
                  text)

    return text


def add_pdf_references(text, document):
    """
    Adds link to pdf when document asks to see the original document.
    """
    document.get_pdf_url()

    def replace_docs(_):
        return '<a href=%s>(ver documento original)</a>' % document.get_pdf_url()

    text = re.sub('\(ver documento original\)', replace_docs, text)

    return text


def docs_regex(types):
    """
    Returns a regex that matches a document.
    """
    return '(%s) n.º ([^\s]+/\d+)(/[A-Z]*)?' % '|'.join([type.name for type in types])


def enum_docs_regex(types):
    type_names = [PLURALS[type.name] for type in types if type.name in PLURALS]
    return '(%s) n.os (.*?) e ([^\s]+/\d+)(/[A-Z]*)?' % '|'.join(type_names)


def _get_enum_documents_query(text, types):
    """
    Returns a Q object representing a query to existing enumerated documents in
    text.
    """
    matches = re.findall(enum_docs_regex(types), text)
    query = Q()
    for name, other_numbers_string, number, number_suffix in matches:
        if number_suffix:
            number += number_suffix

        numbers = re.findall('([^\s]+/\d+)(/[A-Z]*)?', other_numbers_string)
        numbers = [number[0] + number[1] for number in numbers] + [number]
        for number in numbers:
            query = query | Q(type__name=SINGULARS[name], number=number)

    return query


def get_documents(text, types=None):
    """
    Returns a query with all documents a given text refers to.
    """
    text = re.sub(' +', ' ', text)
    from .models import Type, Document
    if types is None:
        types = list(Type.objects.exclude(name__contains='('))

    matches = set(re.findall(docs_regex(types), text))

    if not matches:
        return Document.objects.none()

    query = Q()
    for name, number, number_suffix in matches:
        if number_suffix:
            number += number_suffix
        query = query | Q(type__name=name, number=number)

    query = query | _get_enum_documents_query(text, types)
    return Document.objects.exclude(dr_series='II').filter(query)


def add_references(text):
    """
    This function replaces references of documents with href anchors to
    the respective documents.

    It does:
     1. one hit to get all type names
     2. one pass to get all distinct tuples (type_name, number) in the document
     3. one hit to retrieve all documents with that tuple
     4. one pass to replace all occurrences by anchors.
    """
    from .models import Type
    types = list(Type.objects.exclude(name__contains='('))

    documents = get_documents(text, types).prefetch_related('type')

    # create an inverted index (type_name, number) -> doc
    index = dict([((doc.type.name, doc.number), doc) for doc in documents])

    def replace_doc(name, number, number_suffix):
        """
        Replaces a reference to a document by a href anchor.
        """
        if number_suffix:
            number += number_suffix

        default = '%s n.º %s' % (name, number)

        if (name, number) in index:
            doc = index[(name, number)]
            return '<a class="reference-%d" title="%s" href="%s">%s</a>' \
                   % (doc.id, doc.summary, doc.get_absolute_url(), default)
        return '%s n.º %s' % (name, number)

    def replace_docs(name, other_numbers_string, last_number, last_number_suffix):
        """
        Replaces a reference to multiple documents by href anchors.
        """
        name = SINGULARS[name]
        if last_number_suffix:
            last_number += last_number_suffix

        if (name, last_number) in index:
            doc = index[(name, last_number)]
            last_number = '<a class="reference-%d" title="%s" href="%s">%s</a>' \
                % (doc.id, doc.summary, doc.get_absolute_url(), last_number)

        def replace_enum_single(match):
            number, number_suffix = match.group(1, 2)
            if number_suffix:
                number += number_suffix

            default = number

            if (name, number) in index:
                doc = index[(name, number)]
                return '<a class="reference-%d" title="%s" href="%s">%s</a>' \
                       % (doc.id, doc.summary, doc.get_absolute_url(), default)
            return default

        other_numbers_string = re.sub('([^\s]+/\d+)(/[A-Z]*)?', replace_enum_single, other_numbers_string)
        return '%s n.os %s e %s' % (PLURALS[name], other_numbers_string, last_number)

    def replace(match):
        if match.group(1, 2, 3) != (None, None, None):
            return replace_doc(*match.group(1, 2, 3))
        else:
            return replace_docs(*match.group(4, 5, 6, 7))

    # the order must be compatible with order in `replace`.
    text = re.sub(docs_regex(types) + '|' + enum_docs_regex(types), replace, text)
    return text


hierarchy_priority = ['Anexo',
                      'Parte',
                      'Título',
                      'Capítulo',
                      'Secção',
                      'Sub-Secção',
                      'Artigo',
                      'Número',
                      'Alínea']

hierarchy_classes = {'Anexo': 'anexo',
                     'Parte': 'parte',
                     'Título': 'titulo',
                     'Capítulo': 'capitulo',
                     'Secção': 'seccao',
                     'Sub-Secção': 'subseccao',
                     'Artigo': 'artigo',
                     'Número': 'numero list-unstyled',
                     'Alínea': 'alinea list-unstyled'}

hierarchy_ids = {'Anexo': 'anexo',
                 'Parte': 'parte',
                 'Título': 'titulo',
                 'Capítulo': 'capitulo',
                 'Secção': 'seccao',
                 'Sub-Secção': 'subseccao',
                 'Artigo': 'artigo',
                 'Número': 'numero',
                 'Alínea': 'alinea'}


hierarchy_classes_with_titles = ['anexo', 'parte', 'titulo', 'capitulo',
                                 'seccao', 'subseccao', 'artigo']

hierarchy_html_titles = {'Parte': 'h2',
                         'Título': 'h3',
                         'Capítulo': 'h3',
                         'Secção': 'h4',
                         'Sub-Secção': 'h5',
                         'Anexo': 'h2',
                         'Artigo': 'h5'}

hierarchy_html_lists = {'Número': 'li', 'Alínea': 'li'}

hierarchy_regex = {'Anexo': '^Anexo(.*)',
                   'Parte': '^Parte(.*)',
                   'Título': '^Título(.*)',
                   'Capítulo': '^Capítulo (.*)',
                   'Secção': '^Secção (.*)',
                   'Sub-Secção': '^SUBSecção (.*)',
                   'Artigo': '^Artigo (.*)\.º$',
                   'Número': '^(\d+) - .*',
                   'Alínea': '^(\w+)\) .*',
                   }

formal_hierarchy_elements = ['Anexo', 'Artigo', 'Número', 'Alínea']


def compose_text(document):
    ## normalize all text
    text = normalize(document.text)

    soup = BeautifulSoup(text)

    soup.find('p').extract()  # name
    soup.find('p').extract()  # date

    soup = organize_soup(soup)

    text = str(soup)

    ## create references to same document
    text = add_pdf_references(text, document)

    ## create references to other documents
    text = add_references(text)
    return text


def organize_soup(soup):
    last_element = soup.new_tag('p', **{'text': 'Anexo'})
    soup.append(last_element)

    current_element = dict([(format, None) for format in hierarchy_classes])

    previous_element = None

    def add_element(format_to_move, format_to_receive):
        # if format_to_move is an item of lists
        if format_to_move in hierarchy_html_lists:
            # and format_to_receive does not have a list, we create it:
            if current_element[format_to_receive].contents[-1].name != 'ol':
                # we create the list
                current_element[format_to_receive].append(soup.new_tag('ol'))
            # we add the current_element to the list
            current_element[format_to_receive].contents[-1]\
                .append(current_element[format_to_move])
        else:
            current_element[format_to_receive]\
                .append(current_element[format_to_move])

    body = soup
    for element in body.select('p'):
        for format in hierarchy_priority:
            search = re.search(hierarchy_regex[format], element.text)
            if not search:
                continue

            # moving elements to inside other elements
            format_to_move = format
            format_to_receive_index = hierarchy_priority.index(format) - 1
            while format_to_receive_index != -1:
                format_to_receive = hierarchy_priority[format_to_receive_index]

                if current_element[format_to_receive] is not None and \
                        current_element[format] is not None:
                    add_element(format_to_move, format_to_receive)
                    break
                format_to_receive_index -= 1

            for format_to_move in reversed(hierarchy_priority[
                                           hierarchy_priority.index(format)+1:]):
                if current_element[format_to_move] is None:
                    continue

                for format_to_receive_index in reversed(range(
                        hierarchy_priority.index(format_to_move))):
                    format_to_receive = hierarchy_priority[format_to_receive_index]
                    if current_element[format_to_receive] is not None:
                        add_element(format_to_move, format_to_receive)
                        break

            if format in hierarchy_html_lists:
                current_element[format] = soup.new_tag(
                    hierarchy_html_lists[format],
                    **{'class': hierarchy_classes[format]})
            else:
                current_element[format] = soup.new_tag(
                    'div',
                    **{'class': hierarchy_classes[format]})

            element.replaceWith(current_element[format])
            if format in hierarchy_html_titles:
                current_element_title = soup.new_tag(
                    hierarchy_html_titles[format], **{'class': 'title'})
                current_element[format].append(current_element_title)
                current_element_title.append(element)
            else:
                current_element[format].append(element)

            # Create ids of elements
            if format in formal_hierarchy_elements:
                prefix = ''
                for index in reversed(range(formal_hierarchy_elements.index(format))):
                    temp_format = formal_hierarchy_elements[index]
                    if current_element[temp_format]:
                        prefix = current_element[temp_format]['id'] + '-'
                        break

                sufix = ''
                if search.group(1):
                    sufix = '-' + slugify(search.group(1).strip())
                current_element[format]['id'] = prefix + hierarchy_ids[format] + sufix

                anchor_tag = soup.new_tag('a',
                                          **{'class': 'headerlink',
                                             'href': '#%s' % current_element[
                                                 format]['id']})
                anchor_tag.insert(0, NavigableString(' ¶'))

                if format in hierarchy_html_titles:
                    current_element_title.contents[0].append(anchor_tag)
                else:
                    try:
                        current_element[format].contents[0].contents[0].append(anchor_tag)
                    except AttributeError:
                        current_element[format].contents[0].append(anchor_tag)

            # reset all current_element in lower hierarchy
            for lower_format in hierarchy_priority[hierarchy_priority.index(format)+1:]:
                current_element[lower_format] = None

            break
        else:
            # is just text
            for format in reversed(hierarchy_priority):
                if current_element[format] is not None:
                    current_element[format].append(element)
                    break

            if previous_element and previous_element.parent:
                try:
                    classes = previous_element.parent["class"]
                except KeyError:
                    classes = []
                if 'title' in classes \
                        and previous_element.parent.contents \
                        and previous_element.parent.contents[0] == previous_element:
                    previous_element.parent.append(element)
        previous_element = element

    return soup


def compose_summary(summary):
    from .models import Document

    soup = BeautifulSoup(summary)

    for element in soup.findAll('a'):
        try:
            dre_doc_id = int(element['href'].split('=')[1])
            document = Document.objects.get(dre_doc_id=dre_doc_id)
        except:
            ## other link
            continue
        element['href'] = document.get_absolute_url()
    return soup
