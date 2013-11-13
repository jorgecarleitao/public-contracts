from models import CPVS, Category
import xml.etree.ElementTree as ET


def build_cpvs(file_path='../data/cpv_2008.xml'):
    """
    Builds the CPVS from scratch. It does not construct the hierarchy tree.

    Usage: from contracts.cpvs import build_cpvs; build_cpvs()
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {}
    for child in root:
        data['code'] = child.attrib['CODE']
        data['description_en'] = child.findall("TEXT")[5].text
        data['description_pt'] = child.findall("TEXT")[18].text

        try:
            CPVS.objects.get(code=data['code'])
        except CPVS.DoesNotExist:
            CPVS.objects.create(**data)


def build_tree():
    """
    Builds the hierarchy tree for the CPVS. build_cpvs had to run before.

    Usage: from contracts.cpvs import build_tree; build_tree()
    """
    divisions = CPVS.divisions()

    get = lambda node_id: Category.objects.get(pk=node_id)

    for division in divisions:
        print ">      ", division.code
        div = Category.add_root(code=division.code,
                                description_en=division.description_en,
                                description_pt=division.description_pt)
        for group in division.groups():
            print ">>     ", group.code
            gro = get(div.id).add_child(code=group.code,
                                        description_en=group.description_en,
                                        description_pt=group.description_pt)
            for klass in group.classes():
                print ">>>    ", klass.code
                kla = get(gro.id).add_child(code=klass.code,
                                            description_en=klass.description_en,
                                            description_pt=klass.description_pt)
                for category in klass.categories():
                    print ">>>>   ", category.code
                    cat = get(kla.id).add_child(code=category.code,
                                                description_en=category.description_en,
                                                description_pt=category.description_pt)
                    for sub_category1 in category.sub_categories1():
                        print ">>>>>  ", sub_category1.code
                        sub = get(cat.id).add_child(code=sub_category1.code,
                                                    description_en=sub_category1.description_en,
                                                    description_pt=sub_category1.description_pt)
                        for sub_category2 in sub_category1.sub_categories2():
                            print ">>>>>> ", sub_category2.code
                            sub2 = get(sub.id).add_child(code=sub_category2.code,
                                                         description_en=sub_category2.description_en,
                                                         description_pt=sub_category2.description_pt)
                            for sub_category3 in sub_category2.sub_categories3():
                                print ">>>>>>>", sub_category3.code
                                get(sub2.id).add_child(code=sub_category3.code,
                                                       description_en=sub_category3.description_en,
                                                       description_pt=sub_category3.description_pt)
