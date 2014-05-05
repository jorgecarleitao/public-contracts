# coding=utf-8
import re
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from django.utils.text import slugify

import models


def normalize(text):

    text = ' '.join(text.split())

    ## to substitute <br/> by </p><p>
    text = text.replace(u"<br />", u"<br/>")
    text = text.replace(u"<br/>", u"</p><p>")
    text = text.replace(u"<br >", u"<br>")
    text = text.replace(u"<br>", u"</p><p>")
    text = unicode(text)

    ## strip inside tags
    text = text.replace(u'<p> ', u'<p>')
    text = text.replace(u' </p>', u'</p>')

    text = text.replace(u'ARTIGO', u'Artigo')
    text = text.replace(u'PARTE', u'Parte')
    text = text.replace(u'TÍTULO', u'Título')
    text = text.replace(u'CAPÍTULO', u'Capítulo')
    text = text.replace(u'SECÇÃO', u'Secção')
    text = text.replace(u'ANEXO', u'Anexo')

    # older documents use "Art." instead of "Artigo"; change it
    text = re.sub(u'Art\. (\d+)\.º (.*?)',
                  lambda m: u"Artigo %s.º %s" % m.group(1, 2),
                  text
    )

    # older documents use "Artigo #.º - 1 -" instead of "Artigo #.º 1 -"; change it
    text = re.sub(u'Artigo (\d+)\.º - (.*?)',
                  lambda m: u"Artigo %s.º %s" % m.group(1, 2),
                  text
    )

    # create <p>'s specifically for start of articles
    text = re.sub(u"<p>Artigo (\d+)\.º (.*?)</p>",
                  lambda m: u"<p>Artigo %s.º</p><p>%s</p>" % m.group(1, 2),
                  text)

    ## add blockquote to changes
    text = text.replace(u'» </p>', u'»</p>')
    text = text.replace(u'<p> «', u'<p>«')

    text = re.sub(u"<p>«(.*?)»</p>",
                  lambda m: u"<blockquote><p>%s</p></blockquote>" % m.group(1),
                  text, flags=re.MULTILINE)

    # normalize bullets to "# -" (substituting the ones using #.)
    text = re.sub(ur"<p>(\d+)\.",
                  lambda m: u"<p>%s -" % m.group(1),
                  text)

    return text


def add_pdf_references(text, document):
    """
    Adds link to pdf when document asks to see the original document.
    """
    document.get_pdf_url()

    def replace_docs(match):
        return u'<a href=%s>(ver documento original)</a>' % document.get_pdf_url()

    text = re.sub(u'\(ver documento original\)', replace_docs, text)

    return text


def add_references(text):
    types = list(models.Type.objects.exclude(name__contains='('))

    def create_regex():
        """
        Regex to catch expressions of the form "type.name (\d+).º".
        """
        regex = u'('
        for name in [type.name for type in types]:
            regex += name + u'|'
        regex = regex[:-1]
        regex += ur') n.º (.*?/\d+)'
        return regex

    def replace_docs(match):
        """
        callback of re.sub to substitute the document expression by a anchor with link to the document.
        """
        matched_type_name, matched_number = match.group(1, 2)
        matched_type = next(type for type in types if type.name == matched_type_name)
        matched_number = matched_number.strip()

        default = u'%s n.º %s' % (matched_type_name, matched_number)

        try:
            doc = models.Document.objects.get(type_id=matched_type.id, number=matched_number)
        except models.Document.DoesNotExist:
            return default

        summary_soup = BeautifulSoup(doc.summary)
        return u'<a class="reference-%d" title="%s" href="%s">%s</a>' % (doc.id,
                                                                         summary_soup.getText(),
                                                                         doc.get_absolute_url(),
                                                                         default)

    return re.sub(create_regex(), replace_docs, text)


hierarchy_priority = [u'Anexo',
                      u'Parte',
                      u'Título',
                      u'Capítulo',
                      u'Secção',
                      u'Sub-Secção',
                      u'Artigo',
                      u'Número',
                      u'Alínea']

hierarchy_classes = {u'Anexo': 'anexo',
                     u'Parte': 'parte',
                     u'Título': 'titulo',
                     u'Capítulo': 'capitulo',
                     u'Secção': 'seccao',
                     u'Sub-Secção': 'subseccao',
                     u'Artigo': 'artigo',
                     u'Número': 'numero',
                     u'Alínea': 'alinea'}

hierarchy_classes_with_titles = ['anexo', 'parte', 'titulo', 'capitulo', 'seccao', 'subseccao', 'artigo']

hierarchy_html_titles = {u'Parte': 'h2',
                         u'Título': 'h3',
                         u'Capítulo': 'h3',
                         u'Secção': 'h4',
                         u'Sub-Secção': 'h5',
                         u'Anexo': 'h2',
                         u'Artigo': 'h5'}

hierarchy_html_lists = {u'Número': 'li', u'Alínea': 'li'}

hierarchy_regex = {u'Anexo': u'^Anexo(.*)',
                   u'Parte': u'^Parte(.*)',
                   u'Título': u'^Título(.*)',
                   u'Capítulo': u'^Capítulo (.*)',
                   u'Secção': u'^Secção (.*)',
                   u'Sub-Secção': u'^SUBSecção (.*)',
                   u'Artigo': u'^Artigo (.*)\.º$',
                   u'Número': u'^(\d+) - .*',
                   u'Alínea': u'^(\w+)\) .*',
                   }

formal_hierarchy_elements = [u'Anexo', u'Artigo', u'Número', u'Alínea']


def compose_text(document):
    ## normalize all text
    text = normalize(document.text)

    soup = BeautifulSoup(text)

    soup.find('p').extract()  # name
    soup.find('p').extract()  # date

    soup = organize_soup(soup)

    text = unicode(soup)

    ## create references to same document
    text = add_pdf_references(text, document)

    ## create references to other documents
    text = add_references(text)
    return text


def organize_soup(soup):

    last_element = Tag(soup, 'p', {'text': 'Anexo'})
    soup.append(last_element)

    current_element = dict([(format, None) for format in hierarchy_classes])

    previous_element = None

    def add_element(format_to_move, format_to_receive):
        # if format_to_move is an item of lists
        if format_to_move in hierarchy_html_lists:
            # and format_to_receive does not have a list, we create it:
            if current_element[format_to_receive].contents[-1].name != 'ol':
                # we create the list
                current_element[format_to_receive].append(Tag(soup, 'ol'))
            # we add the current_element to the list
            current_element[format_to_receive].contents[-1].append(current_element[format_to_move])
        else:
            current_element[format_to_receive].append(current_element[format_to_move])

    for element in soup.findAll(True, recursive=False):

        for format in hierarchy_priority:
            search = re.search(hierarchy_regex[format], element.text)
            if not search:
                continue

            # moving elements to inside other elements
            format_to_move = format
            format_to_receive_index = hierarchy_priority.index(format) - 1
            while format_to_receive_index != -1:
                format_to_receive = hierarchy_priority[format_to_receive_index]

                if current_element[format_to_receive] is not None and current_element[format] is not None:
                    add_element(format_to_move, format_to_receive)
                    break
                format_to_receive_index -= 1

            for format_to_move in reversed(hierarchy_priority[hierarchy_priority.index(format)+1:]):
                if current_element[format_to_move] is None:
                    continue

                for format_to_receive_index in reversed(range(hierarchy_priority.index(format_to_move))):
                    format_to_receive = hierarchy_priority[format_to_receive_index]
                    if current_element[format_to_receive] is not None:
                        add_element(format_to_move, format_to_receive)
                        break

            if format in hierarchy_html_lists:
                current_element[format] = Tag(soup, hierarchy_html_lists[format],
                                              {'class': hierarchy_classes[format]})
            else:
                current_element[format] = Tag(soup, 'div',
                                              {'class': hierarchy_classes[format]})

            element.replaceWith(current_element[format])
            if format in hierarchy_html_titles:
                current_element_title = Tag(soup, hierarchy_html_titles[format], {'class': 'title'})
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
                current_element[format]['id'] = prefix + hierarchy_classes[format] + sufix

                anchor_tag = Tag(soup, 'a', {'class': 'headerlink', 'href': u'#%s' % current_element[format]['id']})
                anchor_tag.insert(0, NavigableString(u' ¶'))

                if format in hierarchy_html_titles:
                    current_element_title.contents[0].append(anchor_tag)
                else:
                    try:
                        current_element[format].contents[0].contents[0].append(anchor_tag)
                    except AttributeError:
                        current_element[format].contents[0].append(anchor_tag)

            # reset all current_element in lower hierarchy
            for format in hierarchy_priority[hierarchy_priority.index(format)+1:]:
                current_element[format] = None

            break
        else:
            # is just text
            for format in reversed(hierarchy_priority):
                if current_element[format] is not None:
                    current_element[format].append(element)
                    break

            if previous_element and previous_element.parent:
                try:
                    klass = previous_element.parent["class"]
                except KeyError:
                    klass = None
                if klass == 'title'\
                   and previous_element.parent.contents\
                   and previous_element.parent.contents[0] == previous_element:
                    previous_element.parent.append(element)
        previous_element = element

    return soup


def compose_summary(summary):
    soup = BeautifulSoup(summary)

    for element in soup.findAll('a'):
        try:
            dre_doc_id = int(element['href'].split('=')[1])
            document = models.Document.objects.get(dre_doc_id=dre_doc_id)
        except:
            ## other link
            continue
        element['href'] = document.get_absolute_url()
    return soup
