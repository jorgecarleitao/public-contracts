import xml.etree.ElementTree
import logging

if __name__ == "__main__":
    from main.tools import set_up
    set_up.set_up_django_environment('main.settings_for_schedule')

from contracts.models import Category

logger = logging.getLogger(__name__)


def get_xml():
    """
    Gets the xml file directly from the server.

    This does not work as of May 2014 since the zip is compressed using type 9,
    which is proprietary and Python doesn't support it.
    See http://stackoverflow.com/a/12809847/931303
    """
    from urllib.request import urlopen
    from io import BytesIO
    from zipfile import ZipFile

    request = urlopen('http://simap.europa.eu/news/new-cpv/cpv_2008_xml.zip')
    zipfile = ZipFile(BytesIO(request.read()))

    tree = xml.etree.ElementTree.parse(zipfile.open('cpv_2008.xml'))
    return tree.getroot()


def build_categories(file_directory=''):
    """
    Builds the Categories with tree from the xml file available in:
    http://simap.europa.eu/news/new-cpv/cpv_2008_xml.zip
    """
    file_directory += 'cpv_2008.xml'

    tree = xml.etree.ElementTree.parse(file_directory)
    root = tree.getroot()

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


if __name__ == "__main__":
    build_categories()
