# coding=utf-8
import re
from BeautifulSoup import BeautifulSoup, Tag

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
    print text
    text = re.sub(ur"<p>(\d+)\.",
                  lambda m: u"<p>%s -" % m.group(1),
                  text)

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

        return u'<a class="reference-%d" href=%s>%s</a>' % (doc.id, doc.get_absolute_url(), default)

    return re.sub(create_regex(), replace_docs, text)


def compose_text(document):
    ## normalize all text
    text = normalize(document.text)

    ## create references to other documents
    text = add_references(text)

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

        if current_number and current_number_list is None:
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
            anchor['href'] = document.get_pdf_url()
            anchor.string = u'(ver documento original)'

            element.clear()
            element.append(anchor)

        previous_element = element

    text = unicode(soup)
    return text


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
