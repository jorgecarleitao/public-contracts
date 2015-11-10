import xml.etree.ElementTree

from contracts.models import Category


def get_xml():
    """
    Gets the xml file from the web.
    """
    from urllib.request import urlopen

    request = urlopen('https://raw.githubusercontent.com/data-ac-uk/cpv/master/'
                      'etc/cpv_2008.xml')

    tree = xml.etree.ElementTree.parse(request)

    return tree.getroot()


def _get_data(child):
    return {
        'code': child.attrib['CODE'],
        'description_en': child.find('*[@LANG=\'EN\']').text,
        'description_pt': child.find('*[@LANG=\'PT\']').text,
    }


def _get_depth(code):
    pure_code = code[:-2]
    depth = 1
    while depth != 7:
        if pure_code[depth + 1] == '0':
            break
        depth += 1
    return depth


def _get_parent(code):
    depth = _get_depth(code)
    s = list(code[:-2])
    while depth != 1:
        s[depth] = '0'  # pick the parent code
        try:
            return Category.objects.get(code__startswith="".join(s))
        except Category.DoesNotExist:
            depth -= 1

    return None  # parent not found


def add_category(data):

    parent = _get_parent(data['code'])

    try:
        category = Category.objects.get(code=data['code'])
    except Category.DoesNotExist:
        if parent is None:
            category = Category.add_root(**data)
        else:
            category = parent.add_child(**data)

    return category


def build_categories():
    """
    Builds the Categories the xml file. Takes ~2m.
    """
    for child in get_xml():
        data = _get_data(child)
        add_category(data)
