"""
 This module uses the database from
 http://www.dgterritorio.pt/cartografia_e_geodesia/cartografia/carta_administrativa_oficial_de_portugal__caop_/caop_em_vigor/
 specifically from the excel file
 http://www.dgterritorio.pt/ficheiros/cadastro/caop/caop_download/caop_2014_0/areasfregmundistcaop2014_3

 which was:
 1. each sheet was exported to TSV via "save as..." "UTF-16 Unicode Text" in excel.
 2. each sheet was converted to utf-8 via a text program.
 3. each sheet was saved in
 * `contracts/CAOP_data/Areas_distritos_CAOP2014_utf8.txt`
 * `contracts/CAOP_data/Areas_municipios_CAOP2014_utf8.txt`
 * `contracts/CAOP_data/Areas_freguesias_CAOP2014_utf8.txt`
"""
import csv
import json
import os


NUMBER_OF_DISTRICTS = 29
NUMBER_OF_MUNICIPALITIES = 308
NUMBER_OF_COUNTIES = 3092

CONTRACTS_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CAOP_PATH = os.path.join(CONTRACTS_PATH, 'CAOP_data')


def _get_normalized_districts():
    with open(CAOP_PATH + '/Areas_distritos_CAOP2014_utf8.txt', 'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvin = list(tsvin)[1:]  # ignore first line

        count = 0
        for line in tsvin:
            if line[0] == line[1] == '':
                break
            count += 1
        assert(count == NUMBER_OF_DISTRICTS)
        tsvin = tsvin[:count]

        results = []
        for line in tsvin:
            results.append({
                'COD': line[0],
                'DSG': line[2],
                'area': int(line[3].replace(',', ''))}
            )

    assert(len(results) == NUMBER_OF_DISTRICTS)
    return results


def get_districts():
    file_name = CAOP_PATH + '/caop_districts_normalized.json'
    try:
        with open(file_name, 'r') as in_file:
            data = json.load(in_file)
    except IOError:
        data = _get_normalized_districts()
        with open(file_name, 'w') as out_file:
            json.dump(data, out_file)

    assert(len(data) == NUMBER_OF_DISTRICTS)
    return data


def _get_normalized_municipalities():
    districts = get_districts()

    with open(CAOP_PATH + '/Areas_municipios_CAOP2014_utf8.txt', 'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvin = list(tsvin)[1:]  # ignore first line

        count = 0
        for line in tsvin:
            if line[0] == line[1] == '':
                break
            count += 1
        assert(count == NUMBER_OF_MUNICIPALITIES)
        tsvin = tsvin[:count]

        results = []
        for line in tsvin:
            result = {
                'COD': line[0],
                'DSG': line[5],
                'area': int(line[6].replace(',', ''))}

            # create relation with district
            try:
                district = next(district for district in districts
                                if district['DSG'] == line[4])
            except StopIteration:
                raise IndexError("District not found")

            result['district_COD'] = district['COD']

            results.append(result)

    assert(len(results) == NUMBER_OF_MUNICIPALITIES)
    return results


def get_municipalities():
    file_name = CAOP_PATH + '/caop_municipalities_normalized.json'
    try:
        with open(file_name, 'r') as in_file:
            data = json.load(in_file)
    except IOError:
        data = _get_normalized_municipalities()
        with open(file_name, 'w') as out_file:
            json.dump(data, out_file)

    assert(len(data) == NUMBER_OF_MUNICIPALITIES)
    return data


def _get_normalized_counties():
    municipalities = get_municipalities()
    districts = get_districts()

    # create an inverted index NAME->district
    districts_index = dict()
    for d in districts:
        assert(d['DSG'] not in districts_index)
        districts_index[d['DSG']] = d

    with open(CAOP_PATH + '/Areas_freguesias_CAOP2014_utf8.txt', 'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvin = list(tsvin)[1:]  # ignore first line

        count = 0
        for line in tsvin:
            if line[0] == line[1] == '':
                break
            count += 1
        assert(count == NUMBER_OF_COUNTIES)
        tsvin = tsvin[:count]

        results = []
        for line in tsvin:
            assert(len(line) == 10)
            result = {
                'COD': line[0],
                'DSG': " ".join(line[6].split()),
                'area': int(line[7].replace(',', ''))}

            # build relation
            district = districts_index[line[4]]
            try:
                municipality = next(municipality for municipality in municipalities
                                    if municipality['DSG'] == line[5] and
                                    municipality['district_COD'] == district['COD'])
            except StopIteration:
                raise IndexError("Municipality not found")

            result['municipality_COD'] = municipality['COD']

            results.append(result)

    assert(len(results) == NUMBER_OF_COUNTIES)
    return results


def get_counties():
    file_name = CAOP_PATH + '/caop_counties_normalized.json'
    try:
        with open(file_name, 'r') as in_file:
            data = json.load(in_file)
    except IOError:
        data = _get_normalized_counties()
        with open(file_name, 'w') as out_file:
            json.dump(data, out_file)

    assert(len(data) == NUMBER_OF_COUNTIES)
    return data


if __name__ == '__main__':
    get_districts()
    get_municipalities()
    get_districts()
