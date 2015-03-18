import pickle
from datetime import datetime

from bs4 import BeautifulSoup

from .crawler import AbstractCrawler
from . import models


def parse_paid(value):
    """
    Parses a specific portuguese word "Sim"(=Yes) to a bool.
    """
    if value == 'Sim':
        return True
    else:
        return False


def parse_date(text):
    if not text:
        return None

    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(text, "%Y-%m").date()
        except ValueError:
            return datetime.strptime(text, "%Y").date()


class ConflictsCrawler(AbstractCrawler):

    def __init__(self):

        # Conflicts have different formats in the official website. We restrict to this one,
        # and we will have to think on the next ones.
        self.legislature = 'VII'

        super(AbstractCrawler, self).__init__()
        self._string_formatter = 'http://www.parlamento.pt/DeputadoGP/Paginas/XIIL_RegInteresses.aspx?BID=%d&leg=%s'

        self._activities_file_formatter = 'activities_%d.dat'
        self._social_file_formatter = 'conflicts_%d.dat'

        # Mapping between our categories and id names in the page html
        self._html_prefixes = {'social': 'ctl00_ctl13_g_e4f66c46_a162_4329_83cb_3d7fe77e4b57_ctl00_gvCargosSociais_',
                               'activities': 'ctl00_ctl13_g_e4f66c46_a162_4329_83cb_3d7fe77e4b57_ctl00_gvActividades_'}

        # Mapping between our names and the names in the page html
        self._social_html_mapping = {'position_name': 'lblCargo',
                                     'entity_name': 'lblEntidade',
                                     'start_date': 'lblDataInicio',
                                     'end_date': 'lblDataFim',
                                     'activity': 'lblAreaActividade',
                                     'location': 'lblLocalSede'}

        self._activities_html_mapping = {'activity': 'lblActividade',
                                         'start_date': 'lblDataInicio',
                                         'end_date': 'lblDataFim',
                                         'paid': 'lblRemunerada'}

    @staticmethod
    def format_line_id(line):
        """
        if line < 10, returns '0%d' (e.g. '01', '07') else, returns '%d' (e.g. '10', '43').
        """
        line_string = str(line)
        if line < 10:
            line_string = '0%d' % line_string
        return line_string

    def crawl_conflicts_declaration_social(self, bid, legislature):
        string = self.get(self._string_formatter % (bid, legislature))

        soup = BeautifulSoup(string)

        # for each entry
        line = 2
        entries = []
        while True:
            # build the prefix with line number
            prefix = self._html_prefixes['social'] + 'ctl%s_' % self.format_line_id(line)

            # if line doesn't exist, we stop
            if not soup.find('span', dict(id=prefix + self._social_html_mapping['position_name'])):
                break

            # we populate entries with each datum
            entry = {}
            for key in self._social_html_mapping:
                entry[key] = soup.find('span', dict(id=prefix + self._social_html_mapping[key])).text

            entry['start_date'] = parse_date(entry['start_date'])
            entry['end_date'] = parse_date(entry['end_date'])

            line += 1

            entries.append(entry)

        return entries

    def crawl_conflicts_declaration_activities(self, bid, legislature):
        string = self.get(self._string_formatter % (bid, legislature))

        soup = BeautifulSoup(string)

        # for each entry
        line = 2  # they start from 1, and the first is the header.
        entries = []
        while True:
            # build the prefix with line number
            prefix = self._html_prefixes['activities'] + 'ctl%s_' % self.format_line_id(line)

            # if line doesn't exist, we stop
            if not soup.find('span', dict(id=prefix + self._activities_html_mapping['activity'])):
                break

            # we populate entries with each datum
            entry = {}
            for key in self._activities_html_mapping:
                entry[key] = soup.find('span', dict(id=prefix + self._activities_html_mapping[key])).text

            entry['start_date'] = parse_date(entry['start_date'])
            entry['end_date'] = parse_date(entry['end_date'])
            entry['paid'] = parse_paid(entry['paid'])

            line += 1

            entries.append(entry)

        return entries

    def get_conflict_data(self, bid, legislature, flush_cache):
        file_name = self._social_file_formatter % bid

        data = safe_pickle_load(file_name)

        if data is None or flush_cache:
            f = open(file_name, "w")
            data = self.crawl_conflicts_declaration_social(bid, legislature)
            pickle.dump(data, f)
            f.close()
        return data

    def get_activities_data(self, bid, legislature, flush_cache):
        file_name = self._activities_file_formatter % bid

        data = safe_pickle_load(file_name)

        if data is None or flush_cache:
            f = open(file_name, "w")
            data = self.crawl_conflicts_declaration_activities(bid, legislature)
            pickle.dump(data, f)
            f.close()
        return data

    def crawl_conflicts(self, flush_cache=False):
        for deputy in models.Deputy.objects.filter(is_active=True):
            bid = deputy.official_id
            data = self.get_conflict_data(bid, self.legislature, flush_cache)
            yield data

    def crawl_activities(self, flush_cache=False):
        for deputy in models.Deputy.objects.filter(is_active=True):
            bid = deputy.official_id
            data = self.get_activities_data(bid, self.legislature, flush_cache)
            yield data
