# coding=utf-8
import re
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
