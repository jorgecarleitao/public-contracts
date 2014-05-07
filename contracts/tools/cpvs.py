import xml.etree.ElementTree

from . import set_up
set_up.set_up_django_environment()

from contracts.models import Category


def build_categories(file_path='../'):
    """
    Builds the Categories with tree from the xml file available in:
    http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
    """
    file_path += 'cpv_2008.xml'

    tree = xml.etree.ElementTree.parse(file_path)
    root = tree.getroot()

    data = {}
    count = 0
    for child in root:
        data['code'] = child.attrib['CODE']
        data['description_en'] = child.findall("TEXT")[5].text
        data['description_pt'] = child.findall("TEXT")[18].text
        pure_code = data['code'][:-2]

        # which depth on the tree?
        depth = 1
        #print pure_code
        while depth != 7:
            if pure_code[depth + 1] == '0':
                break
            depth += 1
        #print pure_code, depth

        if depth == 1:
            try:
                category = Category.objects.get(code=data['code'])
                assert depth == category.depth, 'category %s with different depth' % data['code']
            except Category.DoesNotExist:
                Category.add_root(**data)
                print('category %s added' % data['code'])
        else:
            # we need to build the parent code:
            # we will use __startwith, dropping the "-#".
            s = list(pure_code)  # turn string into a mutable object
            s[depth] = '0'  # pick the parent code
            parent_pure_code = "".join(s)
            #print parent_pure_code
            try:
                category = Category.objects.get(code=data['code'])
                assert depth == category.depth, 'category %s with different depth' % data['code']
                assert category.get_parent() == Category.objects.get(code__startswith=parent_pure_code),\
                    'category %s with different parent' % data['code']
            except Category.DoesNotExist:
                try:
                    parent_category = Category.objects.get(code__startswith=parent_pure_code)
                    parent_category.add_child(**data)
                    print('category %s added' % data['code'])
                except Category.DoesNotExist:
                    print('category %s not added because lacks parent' % data['code'])
                    continue

        count += 1

if __name__ == "__main__":
    build_categories()
