# coding=utf-8
from __future__ import unicode_literals

import re
from bs4 import BeautifulSoup, NavigableString, Tag

from django.db.models import Q
from django.utils.text import slugify


PLURALS = {'Decreto-Lei': 'Decretos-Leis',
           'Lei': 'Leis',
           'Portaria': 'Portarias'}

SINGULARS = {'Decretos-Leis': 'Decreto-Lei',
             'Leis': 'Lei',
             'Portarias': 'Portaria'}


def clone(el):
    """
    Returns a copy of a bs4 element `el`.

    Credits to http://stackoverflow.com/a/23058678/931303
    """
    if isinstance(el, NavigableString):
        return type(el)(el)

    copy = Tag(None, el.builder, el.name, el.namespace, el.nsprefix)
    # work around bug where there is no builder set
    # https://bugs.launchpad.net/beautifulsoup/+bug/1307471
    copy.attrs = dict(el.attrs)
    for attr in ('can_be_empty_element', 'hidden'):
        setattr(copy, attr, getattr(el, attr))
    for child in el.contents:
        copy.append(clone(child))
    return copy


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
                   'Artigo': '^Artigo (.*)$',
                   'Número': '^(\d+) - .*',
                   'Alínea': '^(\w+)\) .*',
                   }

formal_hierarchy_elements = ['Anexo', 'Artigo', 'Número', 'Alínea']


def compose_index(text):
    soup = organize_soup(BeautifulSoup(normalize(text)))

    new_soup = BeautifulSoup()

    def _add_to_index(soup, root):
        if soup.find_all('div', recursive=False):
            ul_tag = new_soup.new_tag('ul', **{'class': 'tree'})
        else:
            return None

        for element in soup.find_all('div', recursive=False):
            name = element.contents[0].contents[0].text + ' '
            if len(element.contents[0].contents) >= 2:
                name += element.contents[0].contents[1].text
            name = name.replace(' ¶', '')

            anchor = element.contents[0].contents[0].find('a')
            if anchor:
                tag = new_soup.new_tag('a', **{'href': anchor['href']})
                tag.string = name
            else:
                tag = new_soup.new_tag('h5', **{'class': 'tree-toggler'})
                tag.string = name
            li_tag = new_soup.new_tag('li')
            li_tag.append(tag)
            _add_to_index(element, li_tag)
            ul_tag.append(li_tag)

        root.append(ul_tag)

    _add_to_index(soup, new_soup)
    return new_soup.prettify()


def compose_text(document):
    text = organize_text(document.text)

    ## create references to same document
    text = add_pdf_references(text, document)

    ## create references to other documents
    text = add_references(text)
    return text


def organize_text(text):
    # normalize all text
    text = normalize(text)

    soup = BeautifulSoup(text)

    soup.find('p').extract()  # name
    soup.find('p').extract()  # date

    soup = organize_soup(soup)

    return soup.prettify()


def organize_soup(soup, add_links=True):
    # the current element of the state
    current_element = dict([(format, None) for format in hierarchy_classes])
    previous_element = None

    root = BeautifulSoup()

    def add_element(receiving_element, element):
        """
        Adds the current element of `format_to_move` to `receiving_element`.

        If element to add is an element of a list, create a ordered list
        in the receiving element, and add the element to to it.
        """
        # if format_to_move is an item of lists
        if element.name == 'li':
            # and receiving_element does not have a list, we create it:
            if receiving_element.contents[-1].name != 'ol':
                receiving_element.append(root.new_tag('ol'))

            receiving_element = receiving_element.contents[-1]

        receiving_element.append(element)

    def add_element_to_hierarchy(element, format):
        """
        Adds element of format `format_to_move` to the format above in the
        hierarchy, if any.
        """
        for index in reversed(range(0, hierarchy_priority.index(format))):
            format_to_receive = hierarchy_priority[index]

            if current_element[format_to_receive] is not None:
                add_element(current_element[format_to_receive], element)
                break
        else:
            add_element(root, element)

    def create_element(element, format):
        # create new tag for `div` or `li`.
        if format in hierarchy_html_lists:
            new_element = root.new_tag(
                hierarchy_html_lists[format],
                **{'class': hierarchy_classes[format]})
        else:
            new_element = root.new_tag(
                'div',
                **{'class': hierarchy_classes[format]})

        # and put the element in the newly created tag.
        if format in hierarchy_html_titles:
            # if format is title, create it.
            current_element_title = root.new_tag(
                hierarchy_html_titles[format], **{'class': 'title'})
            current_element_title.append(clone(element))

            new_element.append(current_element_title)
        else:
            new_element.append(clone(element))

        return new_element

    def add_id(new_element, format, format_number):
        prefix = ''
        for index in reversed(range(formal_hierarchy_elements.index(format))):
            temp_format = formal_hierarchy_elements[index]
            if current_element[temp_format]:
                prefix = current_element[temp_format]['id'] + '-'
                break

        suffix = ''
        if format_number:
            suffix = '-' + slugify(format_number)

        new_element['id'] = prefix + hierarchy_ids[format] + suffix

        anchor_tag = root.new_tag('a',
                                  **{'href': '#%s' % new_element['id']})
        anchor_tag.insert(0, NavigableString(' ¶'))

        if format in hierarchy_html_titles:
            new_element.contents[0].contents[0].append(anchor_tag)
        else:
            new_element.contents[0].append(anchor_tag)

    for element in soup:
        if element.name == 'blockquote':
            blockquote = root.new_tag('blockquote')
            blockquote.append(organize_soup(element, add_links=False))
            for format in reversed(hierarchy_priority):
                if current_element[format] is not None:
                    current_element[format].append(blockquote)
                    break
            else:
                root.append(blockquote)
            continue  # blockquote added, ignore rest.
        for format in hierarchy_priority:
            search = re.search(hierarchy_regex[format], element.text)
            if not search:
                continue
            format_number = search.group(1).strip()

            new_element = create_element(element, format)

            if add_links and format in formal_hierarchy_elements:
                add_id(new_element, format, format_number)

            add_element_to_hierarchy(new_element, format)

            current_element[format] = new_element
            # reset all current_element in lower hierarchy
            for lower_format in hierarchy_priority[hierarchy_priority.index(format) + 1:]:
                current_element[lower_format] = None
            break
        else:  # is just text
            new_element = clone(element)

            # previous has contents and is not a Navigatable string and first
            # child has class 'title' => it is a title of the previous element.
            if previous_element and previous_element.contents and \
                    previous_element.contents[0].name is not None and \
                    'title' in previous_element.contents[0].get("class", []):
                previous_element.contents[0].append(new_element)
            else:
                # add to last non-None format
                for format in reversed(hierarchy_priority):
                    if current_element[format] is not None:
                        current_element[format].append(new_element)
                        break
                else:
                    root.append(new_element)

        previous_element = new_element

    return root


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
