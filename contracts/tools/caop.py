"""
This module uses the database from
 https://www.bportugal.pt/pt-PT/Estatisticas/MetodologiaseNomenclaturasEstatisticas/LEFE/Publicacoes/AP_listas.xls

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


NUMBER_OF_DISTRICTS = 29
NUMBER_OF_MUNICIPALITIES = 308
NUMBER_OF_COUNTIES = 3092


# These functions use data from
# http://www.dgterritorio.pt/cartografia_e_geodesia/cartografia/carta_administrativa_oficial_de_portugal__caop_/caop_em_vigor/
# specifically from the excel file
# http://www.dgterritorio.pt/ficheiros/cadastro/caop/caop_download/caop_2014_0/areasfregmundistcaop2014_3
# which was:
# 1. exported to TSV via "save as..." "UTF-16 Unicode Text" in excel.
# 2. converted to utf-8 via a text program.
def normalize_districts_to_json():
    with open('contracts/CAOP_data/Areas_distritos_CAOP2014_utf8.txt', 'r') as tsvin:
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
    with open('contracts/CAOP_data/districts.json', 'w') as outfile:
        json.dump(results, outfile)


def get_districts():
    with open('contracts/CAOP_data/districts.json', 'r') as in_file:
        results = json.load(in_file)

    assert(len(results) == NUMBER_OF_DISTRICTS)
    return results


def normalize_municipalities_to_json():
    districts = get_districts()

    with open('contracts/CAOP_data/Areas_municipios_CAOP2014_utf8.txt', 'r') as tsvin:
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
    with open('contracts/CAOP_data/municipalities.json', 'w') as outfile:
        json.dump(results, outfile)


def get_municipalities():
    with open('contracts/CAOP_data/municipalities.json', 'r') as in_file:
        results = json.load(in_file)

    assert(len(results) == NUMBER_OF_MUNICIPALITIES)
    return results


def normalize_counties_to_json():
    municipalities = get_municipalities()
    districts = get_districts()

    # create an inverted index NAME->district
    districts_index = dict()
    for d in districts:
        assert(d['DSG'] not in districts_index)
        districts_index[d['DSG']] = d

    with open('contracts/CAOP_data/Areas_freguesias_CAOP2014_utf8.txt', 'r') as tsvin:
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
    with open('contracts/CAOP_data/counties.json', 'w') as outfile:
        json.dump(results, outfile)


def get_counties():
    with open('contracts/CAOP_data/counties.json', 'r') as in_file:
        results = json.load(in_file)

    assert(len(results) == NUMBER_OF_COUNTIES)
    return results


if __name__ == '__main__':
    normalize_districts_to_json()
    normalize_municipalities_to_json()
    normalize_counties_to_json()
