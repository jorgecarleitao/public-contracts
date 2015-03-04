"""
This module uses the database from
 https://www.bportugal.pt/pt-PT/Estatisticas/MetodologiaseNomenclaturasEstatisticas/LEFE/Publicacoes/AP_listas.xls

 which was:
 1. exported to TSV via "save as..." "UTF-16 Unicode Text" in excel.
 2. converted to utf-8 via a text program.
 3. saved in `contracts/DGAL_data/bp_list.tsv`
"""

import csv
import datetime
import json

import contracts.tools.caop as caop


def handler(obj):
    # see http://stackoverflow.com/a/2680060/931303
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, ...):
        return ...
    else:
        raise TypeError('Object of type %s with value of %s is not '
                        'JSON serializable' % (type(obj), repr(obj)))


def parse_date(value):
    if value != '':
        for str_format in ('%d/%m/%Y', '%d/%m/%y', '%d-%m-%y', '%d-%m-%Y'):
            try:
                return datetime.datetime.strptime(value, str_format).date()
            except ValueError:
                pass
        else:
            raise ValueError
    return None


def parse_name(value):
    words = value.split()
    # remove syntax errors
    if words[0] in ('MUNICÍPIOS', 'MUNICIPIO', 'MUNÍCIPIO'):
        words[0] = 'MUNICÍPIO'
    elif words[0] == 'CAMARA' and words[1] == 'MUNICIPAL':
        words[0] = 'CÂMARA'
    # add missing 'DE'
    if value == 'CÂMARA MUNICIPAL MACEDO DE CAVALEIROS':
        return 'CÂMARA MUNICIPAL DE MACEDO DE CAVALEIROS'

    return " ".join(words)


def normalize_data():
    with open('contracts/DGAL_data/bp_list.tsv', 'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvin = list(tsvin)
        assert(len(tsvin) == 5890)

        results = []
        for line in tsvin:
            assert(len(line[0]) == 9)
            results.append({
                'NIF': int(line[0]),
                'type': line[1],
                'name': parse_name(line[2]),
                'start_date': parse_date(line[3]),
                'end_date': parse_date(line[4])})

        with open('contracts/DGAL_data/bp_list_normalized.json', 'w') as outfile:
            json.dump(results, outfile, default=handler)


def map_municipality_name(name):
    if name.startswith('D'):
        name = ' '.join(name.split(' ')[1:])
    if name.startswith('CONCELHO DE ') or name.startswith('CONCELHO DO '):
        name = name[len('CONCELHO DE '):]

    mapping = {'BAIAO': 'BAIÃO',
               'CARRAZEDA DE ANSIAES': 'CARRAZEDA DE ANSIÃES',
               'CASTANHEIRA DE PERA': 'CASTANHEIRA DE PÊRA',
               'FIGUEIRO DOS VINHOS': 'FIGUEIRÓ DOS VINHOS',
               'FREIXO DE ESPADA A CINTA': 'FREIXO DE ESPADA À CINTA',
               'RIBEIRA DA PENA': 'RIBEIRA DE PENA',
               'SANTA MARTA DE PENAGUIAO': 'SANTA MARTA DE PENAGUIÃO',
               'TABUA': 'TÁBUA',
               'VILA NOVA DE FAMALICAO': 'VILA NOVA DE FAMALICÃO',
               'VILA NOVA DE FOZ COA': 'VILA NOVA DE FOZ CÔA',
               'MACAO': 'MAÇÃO',
               'LOURINHA': 'LOURINHÃ',
               'NAZARE': 'NAZARÉ',
               'POVOA DE LANHOSO': 'PÓVOA DE LANHOSO',
               'POVOACAO': 'POVOAÇÃO',
               'PRAIA DA VITORIA': 'PRAIA DA VITÓRIA',
               'AGUEDA': 'ÁGUEDA',
               'ALCACER DO SAL': 'ALCÁCER DO SAL',
               'ALFANDEGADA FE': 'ALFÂNDEGA DA FÉ',
               'ALPIARCA': 'ALPIARÇA',
               'ALTER DO CHAO': 'ALTER DO CHÃO',
               'ALVAIAZERE': 'ALVAIÁZERE',
               'BRAGANCA': 'BRAGANÇA',
               'CALHETA - SAO JORGE': 'CALHETA DE SÃO JORGE',
               'EVORA': 'ÉVORA',
               'FERREIRA DO ZEZERE': 'FERREIRA DO ZÊZERE',
               'GOIS': 'GÓIS',
               'LAGOA - AÇORES': 'LAGOA / ILHA DE SÃO MIGUEL (AÇORES)',
               'MEDA': 'MÊDA',
               'MONCAO': 'MONÇÃO',
               'MONTEMOR O NOVO': 'MONTEMOR-O-NOVO',
               'OBIDOS': 'ÓBIDOS',
               'OLIVEIRA DE AZEMEIS': 'OLIVEIRA DE AZEMÉIS',
               'PEDROGAO GRANDE': 'PEDRÓGÃO GRANDE',
               'PONTE DE SÔR': 'PONTE DE SOR',
               'S. BRAS DE ALPORTEL': 'SÃO BRÁS DE ALPORTEL',
               'SANTA COMBA DAO': 'SANTA COMBA DÃO',
               'SAO ROQUE DO PICO': 'SÃO ROQUE DO PICO',
               'SOBRAL DE MONTE AGRACO': 'SOBRAL DE MONTE AGRAÇO',
               'VILA VELHA DE RODAO': 'VILA VELHA DE RÓDÃO',
               'VILA VICOSA': 'VILA VIÇOSA',
               'FUNDAO': 'FUNDÃO',
               'TABUACO': 'TABUAÇO'}
    if name in mapping:
        return mapping[name]
    return name


def _get_municipalities():
    caop_municipalities = caop.get_municipalities()
    caop_districts = caop.get_districts()

    # create a mapping COD->district
    districts_index = dict()
    for d in caop_districts:
        districts_index[d['COD']] = d

    # create a mapping 'DSG / district_DSG' -> municipality
    municipalities_index = dict()
    for m in caop_municipalities:
        key = m['DSG']
        if key in municipalities_index:
            key = '%s / %s' % (m['DSG'], districts_index[m['district_COD']]['DSG'])
        assert(key not in municipalities_index)
        municipalities_index[key] = m

    with open('contracts/DGAL_data/bp_list_normalized.json', 'r') as in_file:
        data = json.load(in_file)

    municipalities = []
    for d in data:
        for name in ('MUNICÍPIO', 'CÂMARA MUNICIPAL'):
            if d['name'].startswith(name):
                name = d['name'][len(name) + 1:]
                name = map_municipality_name(name)

                result = municipalities_index[name].copy()
                result.update(d)
                del result['name']
                municipalities.append(result)
                del municipalities_index[name]
                break

    assert(len(municipalities) == 308)
    return municipalities


def get_municipalities():
    file_name = 'contracts/DGAL_data/municipalities.json'
    try:
        with open(file_name, 'r') as in_file:
            return json.load(in_file)
    except IOError:
        with open(file_name, 'w') as out_file:
            data = _get_municipalities()
            json.dump(data, out_file)
            return data


if __name__ == '__main__':
    normalize_data()
    get_municipalities()
