import re
from datetime import datetime
import logging

import requests
from bs4 import BeautifulSoup

from pt_law_downloader import cache

# Get an instance of a logger
logger = logging.getLogger(__name__)


class AbstractCrawler(object):
    """
    A thin wrapper of request.get with a custom user agent and timeout.
    """
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko)'

    def get_url(self, url):
        response = requests.get(url, headers={'User-agent': self.user_agent},
                                timeout=10)
        return response.text


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

    string = string.strip()
    match = re.search('([XIV]+) \[(.*? a .*?)\]', string)
    number = roman_numerals[match.group(1)]

    dates_match = re.search('(.*?) a ([0-9\-]+)?', match.group(2))

    start = datetime.strptime(dates_match.group(1), "%Y-%m-%d").date()
    if dates_match.group(2) is not None:
        end = datetime.strptime(dates_match.group(2), "%Y-%m-%d").date()
    else:
        end = None

    return number, start, end


def clean_birthday(string):
    if string is None:
        return string
    return datetime.strptime(string.text, "%Y-%m-%d").date()


def clean_education(string):
    if string is None:
        return []
    entries = []
    for each in string.findAll('tr')[1:]:
        text = each.find('span').text
        entries.append(text)
    return entries


def clean_commissions(value):
    if value is None:
        return []
    entries = []
    for each in value.findAll('tr')[1:]:
        entries.append(each.text)
    return entries


def clean_jobs(string):
    if string is None:
        return []
    entries = []
    for each in string.findAll('tr')[1:]:
        if '\n' in each.text:
            for j in each.text.split('\n'):
                if j:
                    entries.append(j.rstrip(' .;'))
        else:
            entries.append(each.text)
    return entries


def clean_current_jobs(string):
    if string is None:
        return []
    entries = []
    for each in string.findAll('tr')[1:]:
        if '\n' in each.text:
            for j in each.text.split('\n'):
                if j:
                    entries.append(j.rstrip(' .;'))
        else:
            entries.append(each.text.rstrip(' ;.'))

    return entries


def clean_awards(value):
    if value is None:
        return []
    entries = []
    for each in value.findAll('tr')[1:]:
        if '\n' in each.text:
            for j in each.text.split('\n'):
                if j:
                    entries.append(j.rstrip(' .;'))
        else:
            entries.append(each.text.rstrip(' ;.'))
    return entries


def clean_mandates(string):
    if string is None:
        return []
    entries = []
    for each in string.findAll('tr')[1:]:
        leg = each.findAll('td')
        l = leg[0].text
        number, start_date, end_date = clean_legislature(l)

        entries.append({'legislature': number,
                        'start_date': start_date,
                        'end_date': end_date,
                        'constituency': leg[3].text,
                        'party': leg[4].text})
    return entries


def clean_text(value):
    if value is None:
        return None
    return value.text


DEPUTY_URL_FORMATTER = 'http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'
HTML_PREFIX = 'ctl00_ctl43_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_'


class DeputiesCrawler(AbstractCrawler):
    _html_mapping = {'name': 'ucNome_rptContent_ctl01_lblText',
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

    _html_element = {'name': 'span',
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

    _validators = {'name': clean_text,
                   'short': clean_text,
                   'birthday': clean_birthday,
                   'party': clean_text,
                   'education': clean_education,
                   'occupation': clean_education,
                   'jobs': clean_jobs,
                   'current_jobs': clean_current_jobs,
                   'commissions': clean_commissions,
                   'awards': clean_awards,
                   'mandates': clean_mandates,
                   }

    @cache('../deputies_html/deputy_{1}.html')
    def get_html(self, bid):
        return self.get_url(DEPUTY_URL_FORMATTER % bid)

    def get_deputy(self, bid):
        soup = BeautifulSoup(self.get_html(bid))

        tester_key = 'name'
        # if name doesn't exist, we exit
        if not soup.find(self._html_element[tester_key],
                         dict(id=HTML_PREFIX + self._html_mapping[tester_key])):
            return {}

        # we populate "entry" with each datum
        entry = {}
        for key in self._html_mapping:
            entry[key] = soup.find(self._html_element[key],
                                   dict(id=HTML_PREFIX + self._html_mapping[key]))

        # and we clean and validate it in place:
        for key in entry:
            entry[key] = self._validators[key](entry[key])
        entry['id'] = bid

        return entry

    def iterate_deputies(self):
        """
        Returns an iterable of deputies dictionaries.

        It stops if the no deputy is found after 1000 trials.
        """
        consecutive_fail_count = 0
        max_consecutive_fail_count = 1000

        bid = 0
        while True:
            entry = self.get_deputy(bid)
            if entry != {}:
                consecutive_fail_count = 0
                yield entry
            else:
                consecutive_fail_count += 1
            bid += 1

            if consecutive_fail_count == max_consecutive_fail_count:
                break
