"""
This module uses the database from
 https://appls.portalautarquico.pt/PortalAutarquico/ResourceLink.aspx?ResourceName=DGAL_Freguesias_2014_V7.xlsx

 which was:
 1. exported to TSV via "save as..." "UTF-16 Unicode Text" in excel.
 2. converted to utf-8 via a text program.
 3. saved in `contracts/DGAL_data/DGAL_Freguesias_2014_V7_utf8.txt`
"""
import csv
import json
import os

import contracts.tools.caop as caop
from contracts.tools.caop import CONTRACTS_PATH

DGAL_PATH = os.path.join(CONTRACTS_PATH, 'DGAL_data')


def normalize_counties_to_json():
    with open(DGAL_PATH + '/DGAL_Freguesias_2014_V7_utf8.txt', 'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvin = list(tsvin)[1:]  # ignore header

        results = []
        for line in tsvin:
            results.append({
                'code': line[0],
                'name': line[1],
                'NIF': int(line[3])}
            )

    # CORVO exist as region but has no county NIF.
    assert(len(results) == caop.NUMBER_OF_COUNTIES - 1)

    with open(DGAL_PATH + '/DGAL_normalized.json', 'w') as outfile:
        json.dump(results, outfile)


def map_county_name(name):
    name = name.replace('MEDA', 'MÊDA')
    name = name.replace('SABOIA', 'SABÓIA')
    name = name.replace('TAINHAS', 'TAÍNHAS')
    name = name.replace('CRISTÓVAL', 'CRISTOVAL')
    name = name.replace('(LAGOA (ALGARVE))', '(LAGOA)')
    name = name.replace('(LAGOA (SÃO MIGUEL))', '(LAGOA)')
    name = name.replace('(CALHETA (MADEIRA))', '(CALHETA)')
    name = name.replace('(CALHETA (SÃO JORGE))', '(CALHETA DE SÃO JORGE)')
    name = name.replace('IGREJA NOVA.', 'IGREJA NOVA')

    mapping = {
        'SÃO JOSÉ (PONTA DELGADA)': 'PONTA DELGADA (SÃO JOSÉ) (PONTA DELGADA)',
        'CARVALHOS (BARCELOS)': 'CARVALHAS (BARCELOS)',
        'TABUA (RIBEIRA BRAVA)': 'TÁBUA (RIBEIRA BRAVA)',
        'LAJEOSA (TONDELA)': 'LAJEOSA DO DÃO (TONDELA)',
        'SERRA D EL-REI (PENICHE)': 'SERRA D\'EL-REI (PENICHE)',
        'VILA NOVA DE SOUTO D EL-REI (LAMEGO)': 'VILA NOVA DE SOUTO D\'EL-REI (LAMEGO)',
        'QUINTA DE SÃO BARTOLOMEU (SABUGAL)': 'QUINTAS DE SÃO BARTOLOMEU (SABUGAL)',
        'SÃO PEDRO DARCOS (PONTE DE LIMA)': 'SÃO PEDRO D\'ARCOS (PONTE DE LIMA)',
        'FREGUESIA DO VALE DO MASSUEIME (PINHEL)': 'VALE DO MASSUEIME (PINHEL)',
        'BORBA DA MONTANHA (CELORICO DE BASTO)': 'BORBA DE MONTANHA (CELORICO DE BASTO)',
        'ESTREITO CÂMARA DE LOBOS (CÂMARA DE LOBOS)': 'ESTREITO DE CÂMARA DE LOBOS (CÂMARA DE LOBOS)',
        'TOPO NOSSA SENHORA DO ROSÁRIO (CALHETA DE SÃO JORGE)': 'TOPO (NOSSA SENHORA DO ROSÁRIO) (CALHETA DE SÃO JORGE)',
        'GEME (VILA VERDE)': 'GÊME (VILA VERDE)',
        'CÔTA (VISEU)': 'COTA (VISEU)',
        'ARGERIZ (VALPAÇOS)': 'ALGERIZ (VALPAÇOS)',
        'SÃO JORGE (VELAS) (VELAS)': 'VELAS (SÃO JORGE) (VELAS)',
        'VIDAGO, ARCOSSÓ, SELHARIZ, VILARINHO PARANHEIRAS (CHAVES)': 'VIDAGO (UNIÃO DAS FREGUESIAS DE VIDAGO, ARCOSSÓ, SELHARIZ E VILARINHO DAS PARANHEIRAS) (CHAVES)',
        'VILA COVA DO COVELO E MARECO (PENALVA DO CASTELO)': 'VILA COVA DO COVELO/MARECO (PENALVA DO CASTELO)',

        'ANGÚSTIAS (HORTA) (HORTA)': 'HORTA (ANGÚSTIAS) (HORTA)',
        'CONCEIÇÃO (HORTA) (HORTA)': 'HORTA (CONCEIÇÃO) (HORTA)',

        'SÃO MIGUEL (VILA FRANCA DO CAMPO)': 'VILA FRANCA DO CAMPO (SÃO MIGUEL) (VILA FRANCA DO CAMPO)',
        'SÃO PEDRO (VILA FRANCA DO CAMPO)': 'VILA FRANCA DO CAMPO (SÃO PEDRO) (VILA FRANCA DO CAMPO)',

        'SÉ (ANGRA DO HEROÍSMO)': 'ANGRA (SÉ) (ANGRA DO HEROÍSMO)',
        'SANTA LUZIA (ANGRA DO HEROÍSMO)': 'ANGRA (SANTA LUZIA) (ANGRA DO HEROÍSMO)',
        'SÃO PEDRO (ANGRA DO HEROÍSMO)': 'ANGRA (SÃO PEDRO) (ANGRA DO HEROÍSMO)',
        'NOSSA SENHORA DA CONCEIÇÃO (ANGRA DO HEROÍSMO)': 'ANGRA (NOSSA SENHORA DA CONCEIÇÃO) (ANGRA DO HEROÍSMO)',
        'SÃO MATEUS (ANGRA DO HEROÍSMO)': 'SÃO MATEUS DA CALHETA (ANGRA DO HEROÍSMO)',

        'SANTA CRUZ (LAGOA)': 'LAGOA (SANTA CRUZ) (LAGOA)',
        'NOSSA SENHORA DO ROSÁRIO (LAGOA)': 'LAGOA (NOSSA SENHORA DO ROSÁRIO) (LAGOA)',

        'SÃO PEDRO (PONTA DELGADA)': 'PONTA DELGADA (SÃO PEDRO) (PONTA DELGADA)',
        'SANTA LUZIA (FUNCHAL)': 'FUNCHAL (SANTA LUZIA) (FUNCHAL)',
        'SANTA MARIA MAIOR (FUNCHAL)': 'FUNCHAL (SANTA MARIA MAIOR) (FUNCHAL)',
        'SÃO PEDRO (FUNCHAL)': 'FUNCHAL (SÃO PEDRO) (FUNCHAL)',
        'SÉ (FUNCHAL)': 'FUNCHAL (SÉ) (FUNCHAL)',

        'PONTE DA BARCA, V.N. MUÍA, PAÇO VEDRO MAGALHÃES (PONTE DA BARCA)': 'PONTE DA BARCA, VILA NOVA DE MUÍA E PAÇO VEDRO DE MAGALHÃES (PONTE DA BARCA)',
        'SÃO FACUNDO E VALE DE MÓS (ABRANTES)': 'SÃO FACUNDO E VALE DAS MÓS (ABRANTES)',
        'SANTO AGOSTINHO E SÃO JOÃO BAPTISTA E SANTO AMADOR (MOURA)': 'MOURA (SANTO AGOSTINHO E SÃO JOÃO BAPTISTA) E SANTO AMADOR (MOURA)',
        'PORTO DE MÓS-SÃO JOÃO BAPTISTA E SÃO PEDRO (PORTO DE MÓS)': 'PORTO DE MÓS - SÃO JOÃO BAPTISTA E SÃO PEDRO (PORTO DE MÓS)',
        'BARCELOS, V.BOA, V.FRESCAINHA (BARCELOS)': 'BARCELOS, VILA BOA E VILA FRESCAINHA (SÃO MARTINHO E SÃO PEDRO) (BARCELOS)',
        'A VER-O-MAR, AMORIM E TERROSO (PÓVOA DE VARZIM)': 'AVER-O-MAR, AMORIM E TERROSO (PÓVOA DE VARZIM)',
        'ATALAIA E ALTO-ESTANQUEIRO-JARDIA (MONTIJO)': 'ATALAIA E ALTO ESTANQUEIRO-JARDIA (MONTIJO)',
        'NOSSA SENHORA DA CONCEIÇÃO, SÃO PEDRO E SÃO DINIS (VILA REAL)': 'VILA REAL (NOSSA SENHORA DA CONCEIÇÃO, SÃO PEDRO E SÃO DINIS) (VILA REAL)',
        'NOSSA SENHORA DA CONCEIÇÃO E DE SÃO BARTOLOMEU (VILA VIÇOSA)': 'NOSSA SENHORA DA CONCEIÇÃO E SÃO BARTOLOMEU (VILA VIÇOSA)',
        'PANÓIAS E CONCEIÇÃO (OURIQUE)': 'PANOIAS E CONCEIÇÃO (OURIQUE)',
        'SOUTO DE CARPALHOSA E ORTIGOSA (LEIRIA)': 'SOUTO DA CARPALHOSA E ORTIGOSA (LEIRIA)',
        'SÃO PEDRO E SANTA MARIA E VILA BOA DO MONDEGO (CELORICO DA BEIRA)': 'CELORICO (SÃO PEDRO E SANTA MARIA) E VILA BOA DO MONDEGO (CELORICO DA BEIRA)',
        'SOBREIRÓ DE BAIXO E ALVAREDOS (VINHAIS)': 'SOBREIRO DE BAIXO E ALVAREDOS (VINHAIS)',
        'SÃO SALVADOR, VILA FONCHE E PARADA (ARCOS DE VALDEVEZ)': 'ARCOS DE VALDEVEZ (SALVADOR), VILA FONCHE E PARADA (ARCOS DE VALDEVEZ)',
        'S.SEBASTIÃO DA GIESTEIRA E N.S. DA BOA FÉ (ÉVORA)': 'SÃO SEBASTIÃO DA GIESTEIRA E NOSSA SENHORA DA BOA FÉ (ÉVORA)',
        'OVAR, S.JOÃO, ARADA E S.VICENTE DE PEREIRA JUSÃ (OVAR)': 'OVAR, SÃO JOÃO, ARADA E SÃO VICENTE DE PEREIRA JUSÃ (OVAR)',
        'PLANALTO DE MONFORTE  (OUCIDRES E BOBADELA) (CHAVES)': 'PLANALTO DE MONFORTE (UNIÃO DAS FREGUESIAS DE OUCIDRES E BOBADELA) (CHAVES)',
        'S.PEDRO E SANTIAGO, S.MARIA E S.MIGUEL, E MATACÃES (TORRES VEDRAS)': 'TORRES VEDRAS (SÃO PEDRO, SANTIAGO, SANTA MARIA DO CASTELO E SÃO MIGUEL) E MATACÃES (TORRES VEDRAS)',
        'SALVADOR E SANTO ALEIXO DE ALÉM-TÂMEGA (RIBEIRA DE PENA)': 'RIBEIRA DE PENA (SALVADOR) E SANTO ALEIXO DE ALÉM-TÂMEGA (RIBEIRA DE PENA)',
        'S.MARIA, S.MIGUEL, S.MARTINHO, S.PEDRO PENAFERRIM (SINTRA)': 'SINTRA (SANTA MARIA E SÃO MIGUEL, SÃO MARTINHO E SÃO PEDRO DE PENAFERRIM) (SINTRA)',
        'OEIRAS E S.JULIÃO DA BARRA, PAÇO DE ARCOS E CAXIAS (OEIRAS)': 'OEIRAS E SÃO JULIÃO DA BARRA, PAÇO DE ARCOS E CAXIAS (OEIRAS)',
        'S.JULIÃO, N.S. DA ANUNCIADA E S.MARIA DA GRAÇA (SETÚBAL)': 'SETÚBAL (SÃO JULIÃO, NOSSA SENHORA DA ANUNCIADA E SANTA MARIA DA GRAÇA) (SETÚBAL)',
        'N.S. CONCEIÇÃO, S.BRÁS MATOS, JUROMENHA (ALANDROAL)': 'ALANDROAL (NOSSA SENHORA DA CONCEIÇÃO), SÃO BRÁS DOS MATOS (MINA DO BUGALHO) E JUROMENHA (NOSSA SENHORA DO LORETO) (ALANDROAL)',
        'N.S. DA TOUREGA E N.S. DE GUADALUPE (ÉVORA)': 'NOSSA SENHORA DA TOUREGA E NOSSA SENHORA DE GUADALUPE (ÉVORA)',
        'MELRES E MÊDAS (GONDOMAR)': 'MELRES E MEDAS (GONDOMAR)',
        'MARGARIDE, VÁRZEA, LAGARES, VARZIELA, MOURE (FELGUEIRAS)': 'MARGARIDE (SANTA EULÁLIA), VÁRZEA, LAGARES, VARZIELA E MOURE (FELGUEIRAS)',
        'GONDOMIL E SAFINS (VALENÇA)': 'GONDOMIL E SANFINS (VALENÇA)',
        'GERAZ DO LIMA (S.MARIA, S.LEOCÁDIA, MOREIRA), DEÃO (VIANA DO CASTELO)': 'GERAZ DO LIMA (SANTA MARIA, SANTA LEOCÁDIA E MOREIRA) E DEÃO (VIANA DO CASTELO)',
        'S.MIG. PINHEIRO, S.PEDRO SOLIS, S.SEBASTIÃO CARROS (MÉRTOLA)': 'SÃO MIGUEL DO PINHEIRO, SÃO PEDRO DE SOLIS E SÃO SEBASTIÃO DOS CARROS (MÉRTOLA)',
        'PINHEIRO DE COJA E MÊDA DE MOUROS (TÁBUA)': 'PINHEIRO DE COJA E MEDA DE MOUROS (TÁBUA)',
        'NOSSA SENHORA DO PÓPULO, COTO E SÃO GREGÓRIO (CALDAS DA RAINHA)': 'CALDAS DA RAINHA - NOSSA SENHORA DO PÓPULO, COTO E SÃO GREGÓRIO (CALDAS DA RAINHA)',
        'CEDOFEITA, ILDEFONSO, SÉ, MIRAGAIA, NICOLAU, VITÓRIA (PORTO)': 'CEDOFEITA, SANTO ILDEFONSO, SÉ, MIRAGAIA, SÃO NICOLAU E VITÓRIA (PORTO)',
        'CAMPO, S.SALVADOR CAMPO, NEGRELOS (SANTO TIRSO)': 'CAMPO (SÃO MARTINHO), SÃO SALVADOR DO CAMPO E NEGRELOS (SÃO MAMEDE) (SANTO TIRSO)',
        'AZINHAL, PEVA E VALE VERDE (ALMEIDA)': 'AZINHAL, PEVA E VALVERDE (ALMEIDA)',
        'FREIXEDA TORRÃO, QUINTÃ PÊRO MARTINS, PENHA (FIGUEIRA DE CASTELO RODRIGO)': 'FREIXEDA DO TORRÃO, QUINTÃ DE PÊRO MARTINS E PENHA DE ÁGUIA (FIGUEIRA DE CASTELO RODRIGO)',
        'CALDAS DE SÃO JORGE E DE PIGEIROS (SANTA MARIA DA FEIRA)': 'CALDAS DE SÃO JORGE E PIGEIROS (SANTA MARIA DA FEIRA)',
        'FUNDÃO, VALVERDE, DONAS, A. JOANES, A. NOVA CABO (FUNDÃO)': 'FUNDÃO, VALVERDE, DONAS, ALDEIA DE JOANES E ALDEIA NOVA DO CABO (FUNDÃO)',
        'FREIXIANDA, RIBEIRA DO FARRIO E FORMIGAIS (OURÉM)': 'FREIXIANDA, RIBEIRA DO FÁRRIO E FORMIGAIS (OURÉM)',
        'ESTÔMBAR E PARCHAL  (LAGOA)': 'ESTÔMBAR E PARCHAL (LAGOA)',
        'LOBRIGOS (S. MIGUEL E S. JOÃO BAPTISTA) E SANHOANE (SANTA MARTA DE PENAGUIÃO)': 'LOBRIGOS (SÃO MIGUEL E SÃO JOÃO BAPTISTA) E SANHOANE (SANTA MARTA DE PENAGUIÃO)',
        'MANIQUE DO INTENDENTE, V.N.DE S.PEDRO E MAÇUSSA (AZAMBUJA)': 'MANIQUE DO INTENDENTE, VILA NOVA DE SÃO PEDRO E MAÇUSSA (AZAMBUJA)',
        'N.S. DA VILA, N.S. DO BISPO E SILVEIRAS (MONTEMOR-O-NOVO)': 'NOSSA SENHORA DA VILA, NOSSA SENHORA DO BISPO E SILVEIRAS (MONTEMOR-O-NOVO)',
        'MARVILA, RIBEIRA SANTARÉM, S.SALVADOR, S.NICOLAU (SANTARÉM)': 'SANTARÉM (MARVILA), SANTA IRIA DA RIBEIRA DE SANTARÉM, SANTARÉM (SÃO SALVADOR) E SANTARÉM (SÃO NICOLAU) (SANTARÉM)',
        'SÃO MARTINHO DE ANTA E PARADELA DE GUIÃES (SABROSA)': 'SÃO MARTINHO DE ANTAS E PARADELA DE GUIÃES (SABROSA)',
        'SANTIAGO DO CACÉM, S.CRUZ E S.BARTOLOMEU DA SERRA (SANTIAGO DO CACÉM)': 'SANTIAGO DO CACÉM, SANTA CRUZ E SÃO BARTOLOMEU DA SERRA (SANTIAGO DO CACÉM)',
        'SANTIAGO E S.SIMÃO DE LITÉM E ALBERGARIA DOS DOZE (POMBAL)': 'SANTIAGO E SÃO SIMÃO DE LITÉM E ALBERGARIA DOS DOZE (POMBAL)',
        'PROVESENDE, GOUVÃES DOURO E S. CRISTÓVÃO DOURO (SABROSA)': 'PROVESENDE, GOUVÃES DO DOURO E SÃO CRISTÓVÃO DO DOURO (SABROSA)',
        'SÃO JOÃO BAPTISTA E SANTA MARIA DOS OLIVAIS (TOMAR)': 'TOMAR (SÃO JOÃO BAPTISTA) E SANTA MARIA DOS OLIVAIS (TOMAR)',
        'O. AZEMÉIS, RIBA-UL, UL, MACINHATA SEIXA, MADAIL (OLIVEIRA DE AZEMÉIS)': 'OLIVEIRA DE AZEMÉIS, SANTIAGO DA RIBA-UL, UL, MACINHATA DA SEIXA E MADAIL (OLIVEIRA DE AZEMÉIS)',
        'TRANCOSO  (SÃO PEDRO E SANTA MARIA) E SOUTO MAIOR (TRANCOSO)': 'TRANCOSO (SÃO PEDRO E SANTA MARIA) E SOUTO MAIOR (TRANCOSO)',
        'LAGOA E CARVOEIRO  (LAGOA)': 'LAGOA E CARVOEIRO (LAGOA)',
        'SANTA MARIA MAIOR E MONSERRATE E MEADELA (VIANA DO CASTELO)': 'VIANA DO CASTELO (SANTA MARIA MAIOR E MONSERRATE) E MEADELA (VIANA DO CASTELO)',
        'CONCEIÇÃO (RIBEIRA GRANDE)': 'RIBEIRA GRANDE (CONCEIÇÃO) (RIBEIRA GRANDE)',
        'SÉ NOVA, SANTA CRUZ, ALMEDINA E SÃO BARTOLOMEU (COIMBRA)': 'COIMBRA (SÉ NOVA, SANTA CRUZ, ALMEDINA E SÃO BARTOLOMEU) (COIMBRA)',
        'VALE MENDIZ, CASAL LOIVOS, VILARINHO COTAS (ALIJÓ)': 'VALE DE MENDIZ, CASAL DE LOIVOS E VILARINHO DE COTAS (ALIJÓ)',
        'ST.TIRSO, COUTO (S.CRISTINA E S.MIGUEL) E BURGÃES (SANTO TIRSO)': 'SANTO TIRSO, COUTO (SANTA CRISTINA E SÃO MIGUEL) E BURGÃES (SANTO TIRSO)',
        'SANTA MARIA DO CASTELO E SANTIAGO E SANTA SUSANA (ALCÁCER DO SAL)': 'ALCÁCER DO SAL (SANTA MARIA DO CASTELO E SANTIAGO) E SANTA SUSANA (ALCÁCER DO SAL)'
        }

    if name in mapping:
        return mapping[name]

    if 'PAUL DO MAR' in name:
        name = name.replace('PAUL', 'PAÚL')

    elif 'PANÓIAS DE CIMA' in name:
        name = name.replace('PANÓIAS', 'PANOIAS')
    elif 'SANTA BÁRBARA (MANADAS)' in name:
        name = name.replace('SANTA BÁRBARA (MANADAS)', 'MANADAS (SANTA BÁRBARA)')

    elif 'PONTA DELGADA (SANTA CLARA)' in name:
        name = name.replace('PONTA DELGADA (SANTA CLARA)',
                            'SANTA CLARA')

    elif 'VALE REMÍGIO' in name:
        name = name.replace('VALE REMÍGIO', 'VALE DE REMÍGIO')
    elif 'VIATODOS, GRIMANCELOS, MINHOTÃES, MONTE FRALÃES (BARCELOS)' in name:
        name = name.replace('MINHOTÃES, MONTE FRALÃES', 'MINHOTÃES E MONTE DE FRALÃES')
    elif 'URRÓS E PEREDO DOS CASTELHANOS' in name:
        name = name.replace('URRÓS', 'URROS')

    return name


def _get_counties():
    caop_counties = caop.get_counties()
    caop_municipalities = caop.get_municipalities()

    # create a mapping COD -> municipality
    municipalities_index = dict()
    for d in caop_municipalities:
        municipalities_index[d['COD']] = d

    # create a mapping 'county_DSG (municipality_DSG)' -> county
    counties_index = dict()
    for c in caop_counties:
        mun = municipalities_index[c['municipality_COD']]
        key = '%s (%s)' % (c['DSG'], mun['DSG'])
        assert(key not in counties_index)
        counties_index[key] = c

    all_keys = set(counties_index.keys())

    with open(DGAL_PATH + '/DGAL_normalized.json', 'r') as in_file:
        data = json.load(in_file)

    counties = []
    keys_found = set()
    for d in data:
        name = map_county_name(d['name'].upper())

        for prefix in ('',
                       'UNIÃO DE FREGUESIAS DE ',
                       'UNIÃO DAS FREGUESIAS DO ',
                       'UNIÃO DAS FREGUESIAS DE ',
                       'UNIÃO DAS FREGUESIAS DA ',
                       'UNIÃO DAS FREGUESIAS DAS '):
            if prefix + name in all_keys:
                county = counties_index[prefix + name]
                keys_found.add(prefix + name)
                break
        else:
            raise IndexError('%s not found.' % name)

        result = d.copy()
        del result['name']
        result.update(county)

        counties.append(result)

    missing = all_keys - keys_found

    # "CORVO" region does not have county
    assert(len(missing) == 1)
    assert(missing.pop() == 'CORVO (CORVO)')

    return counties


def get_counties():
    file_name = DGAL_PATH + '/counties.json'
    try:
        with open(file_name, 'r') as in_file:
            return json.load(in_file)
    except IOError:
        with open(file_name, 'w') as out_file:
            data = _get_counties()
            json.dump(data, out_file)
            return data


if __name__ == '__main__':
    normalize_counties_to_json()
    get_counties()
