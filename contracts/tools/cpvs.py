import xml.etree.ElementTree
import logging

from contracts.models import Category

logger = logging.getLogger(__name__)


def get_xml():
    """
    Gets the xml file from the web.
    """
    from urllib.request import urlopen

    request = urlopen('https://raw.githubusercontent.com/data-ac-uk/cpv/master/etc/cpv_2008.xml')

    tree = xml.etree.ElementTree.parse(request)

    return tree.getroot()


def build_categories():
    """
    Builds the Categories with tree from the xml file available in:
    http://simap.europa.eu/news/new-cpv/cpv_2008_xml.zip
    """
    root = get_xml()

    data = {}
    for child in root:
        data['code'] = child.attrib['CODE']
        data['description_en'] = child.findall("TEXT")[5].text
        data['description_pt'] = child.findall("TEXT")[18].text
        pure_code = data['code'][:-2]

        # which depth on the tree?
        depth = 1
        while depth != 7:
            if pure_code[depth + 1] == '0':
                break
            depth += 1

        if depth == 1:
            try:
                category = Category.objects.get(code=data['code'])
                assert depth == category.depth, 'category %s with different depth' % data['code']
            except Category.DoesNotExist:
                Category.add_root(**data)
                logger.info('category %s added', data['code'])
        else:
            # we need to build the parent code:
            # we will use __startwith, dropping the "-#".
            s = list(pure_code)  # turn string into a mutable object
            s[depth] = '0'  # pick the parent code
            parent_pure_code = "".join(s)

            try:
                category = Category.objects.get(code=data['code'])
                assert depth == category.depth, 'category %s with different depth' % data['code']
                assert category.get_parent() == Category.objects.get(code__startswith=parent_pure_code),\
                    'category %s with different parent' % data['code']
            except Category.DoesNotExist:
                try:
                    parent_category = Category.objects.get(code__startswith=parent_pure_code)
                    parent_category.add_child(**data)
                    logger.info('category %s added', data['code'])
                except Category.DoesNotExist:
                    logger.warning('category %s not added because lacks parent', data['code'])
                    continue
