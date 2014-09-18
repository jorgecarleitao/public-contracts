import pickle
import os
import re
from datetime import datetime
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

import requests.exceptions
from bs4 import BeautifulSoup

from contracts.crawler import AbstractCrawler


def safe_pickle_load(file_name):
    """
    Given a file name, returns the unpickled content of the file or None if any exception.
    """
    try:
        f = open(file_name, "r")
        try:
            data = pickle.load(f)
        except EOFError:
            data = None
        finally:
            f.close()
    except IOError:
        data = None

    return data


def clean_legislature(string):
    """
    Parses a string into a legislature (integer) and dates (beginning and end).
    """

    roman_numerals = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
        'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
        'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    }

    string = string.replace('&nbsp;', '')
    number, dates = string.split('[')
    number = roman_numerals[number.strip()]
    dates = dates.strip(' ]')
    if len(dates.split(' a ')) == 2:
        start, end = dates.split(' a ')
    else:
        start = dates.split(' a ')[0]
        end = ''
    if start.endswith(' a'):
        start = start.replace(' a', '')
    return number, start, end


class DeputiesCrawler(AbstractCrawler):
    def __init__(self):
        super(DeputiesCrawler, self).__init__()

        self._deputy_url_formatter = 'http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'

        self._html_prefix = 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_'

        self._html_mapping = {'name': 'ucNome_rptContent_ctl01_lblText',
                              'short': 'lblNomeDeputado',
                              'birthday': 'ucDOB_rptContent_ctl01_lblText',
                              'party': 'lblPartido',
                              'occupation': 'pnlProf',
                              'education': 'pnlHabilitacoes',
                              'current_jobs': 'pnlCargosDesempenha',
                              'jobs': 'pnlCargosExercidos',
                              'awards': 'pnlCondecoracoes',
                              'commissions': 'pnlComissoes',
                              'mandates': 'gvTabLegs'}

        self._html_element = {'name': 'span',
                              'short': 'span',
                              'birthday': 'span',
                              'party': 'span',
                              'occupation': 'div',
                              'education': 'div',
                              'current_jobs': 'div',
                              'jobs': 'div',
                              'awards': 'div',
                              'commissions': 'div',
                              'mandates': 'table'}

        self.data_directory = '../deputies_data/'

    def crawl_deputy(self, bid):
        url = self._deputy_url_formatter % bid
        soup = BeautifulSoup(self.goToPage(url))

        tester_key = 'name'
        # if name doesn't exist, we exit
        if not soup.find(self._html_element[tester_key], dict(id=self._html_prefix + self._html_mapping[tester_key])):
            return {}

        # we populate "entry" with each datum
        entry = {}
        for key in self._html_mapping:
            entry[key] = soup.find(self._html_element[key],
                                   dict(id=self._html_prefix + self._html_mapping[key])) or None
        entry['name'] = entry['name'].text

        # and we clean and validate it in place:
        entry['id'] = bid
        entry['retrieval_date'] = datetime.utcnow().isoformat()

        if entry['short'] is not None:
            entry['short'] = entry['short'].text
        if entry['birthday'] is not None:
            entry['birthday'] = datetime.strptime(entry['birthday'].text, "%Y-%m-%d").date()
        if entry['party'] is not None:
            entry['party'] = entry['party'].text

        if entry['education'] is not None:
            entries = []
            for each in entry['education'].findAll('tr')[1:]:
                text = each.find('span').text
                entries.append(text)
            entry['education'] = entries
        else:
            entry['education'] = []

        if entry['occupation'] is not None:
            entries = []
            for each in entry['occupation'].findAll('tr')[1:]:
                entries.append(each.text)
            entry['occupation'] = entries
        else:
            entry['occupation'] = []

        if entry['jobs']:
            entries = []
            for each in entry['jobs'].findAll('tr')[1:]:
                if '\n' in each.text:
                    for j in each.text.split('\n'):
                        if j:
                            entries.append(j.rstrip(' .;'))
                else:
                    entries.append(each.text)
            entry['jobs'] = entries
        else:
            entry['jobs'] = []

        if entry['current_jobs'] is not None:
            entries = []
            for each in entry['current_jobs'].findAll('tr')[1:]:
                if '\n' in each.text:
                    for j in each.text.split('\n'):
                        if j:
                            entries.append(j.rstrip(' .;'))
                else:
                    entries.append(each.text.rstrip(' ;.'))
            entry['current_jobs'] = entries
        else:
            entry['current_jobs'] = []

        if entry['commissions'] is not None:
            entries = []
            for each in entry['commissions'].findAll('tr')[1:]:
                entries.append(each.text)
            entry['commissions'] = entries
        else:
            entry['commissions'] = []

        if entry['awards']:
            entries = []
            for each in entry['awards'].findAll('tr')[1:]:
                if '\n' in each.text:
                    for j in each.text.split('\n'):
                        if j:
                            entries.append(j.rstrip(' .;'))
                else:
                    entries.append(each.text.rstrip(' ;.'))
            entry['awards'] = entries
        else:
            entry['awards'] = []

        if entry['mandates']:
            entries = []
            for each in entry['mandates'].findAll('tr')[1:]:
                leg = each.findAll('td')
                l = leg[0].text
                number, start_date, end_date = clean_legislature(l)

                entries.append({'legislature': number,
                                'start_date': start_date,
                                'end_date': end_date,
                                'constituency': leg[3].text,
                                'party': leg[4].text})
            entry['mandates'] = entries
        else:
            entry['mandates'] = []

        return entry

    def get_deputy(self, bid, flush_cache=False):
        logger.info('retrieving bid %d', bid)
        file_name = self.data_directory + 'deputy_%d.dat' % bid
        data = safe_pickle_load(file_name)

        if data is None or flush_cache:
            try:
                data = self.crawl_deputy(bid)
            except:
                logger.exception('Not able to retrieve bid %d', bid)
                raise

            f = open(file_name, "w")
            pickle.dump(data, f)
            f.close()
        return data

    def get_last_bid(self):
        regex = re.compile(r"deputy_(\d+).dat")
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s' % self.data_directory) if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x), reverse=True)
        if len(files):
            return files[0]
        else:
            return 0

    def get_deputies(self, flush_cache=False):
        """
        Returns an iterable of deputies data. If flush_cache is True,
        cached data is updated.
        """
        bid = 0
        while True:
            entry = self.get_deputy(bid, flush_cache)
            if entry != {}:
                yield entry
            bid += 1

    def get_deputies_list(self, bid_list):
        """
        Returns an iterable of deputies data from the bid list.
        Used to update entries.
        """
        for bid in bid_list:
            entry = self.get_deputy(bid, flush_cache=True)
            yield entry

    def get_new_deputies(self):
        bid = self.get_last_bid()
        while True:
            try:
                entry = self.get_deputy(bid, True)
            except requests.exceptions.ConnectionError:
                if 'User-agent' in self.request_headers:
                    logger.warning("removed header")
                    self.request_headers['User-agent'].pop()
                else:
                    logger.warning("added header")
                    self.request_headers['User-agent'] = self.user_agent
                entry = self.get_deputy(bid, True)
            if entry != {}:
                yield entry
            bid += 1
