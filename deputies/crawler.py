import pickle
from BeautifulSoup import BeautifulSoup
from datetime import datetime
import mechanize as mc
import cookielib


class AbstractCrawler(object):

    class NoMoreEntriesError:
        pass

    def __init__(self):
        # Browser
        br = mc.Browser()

        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        # Browser options
        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        br.set_handle_refresh(mc._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)

        # User-Agent. For choosing one, use for instance this with your browser: http://whatsmyuseragent.com/
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) '
                                        'AppleWebKit/537.36 (KHTML, like Gecko)'),
                         ('Range', "items=0-24")]
        self.browser = br

    def goToPage(self, url):
        response = self.browser.open(url)
        return response.read()


crawler = AbstractCrawler()

DEFAULT_MAX = 4600

ROMAN_NUMERALS = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    }

DATASETS = '../../datasets/'
URL_DEPS_ACTIVOS='http://www.parlamento.pt/DeputadoGP/Paginas/DeputadosemFuncoes.aspx'
FORMATTER_URL_BIO_DEP='http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'


def parse_legislature(s):
    s = s.replace('&nbsp;', '')
    number, dates = s.split('[')
    number = ROMAN_NUMERALS[number.strip()]
    dates = dates.strip(' ]')
    if len(dates.split(' a ')) == 2:
        start, end = dates.split(' a ')
    else:
        start = dates.split(' a ')[0]
        end = ''
    if start.endswith(' a'):
        start = start.replace(' a', '')
    return number, start, end


def parse_deputy(id):
    url = FORMATTER_URL_BIO_DEP % id
    soup = BeautifulSoup(crawler.goToPage(url))

    id_prefix = 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_'

    name = soup.find('span', dict(id=id_prefix+'ucNome_rptContent_ctl01_lblText'))
    short = soup.find('span', dict(id=id_prefix+'lblNomeDeputado'))
    birthdate = soup.find('span', dict(id=id_prefix+'ucDOB_rptContent_ctl01_lblText'))
    party = soup.find('span', dict(id=id_prefix+'lblPartido'))
    occupation = soup.find('div', dict(id=id_prefix+'pnlProf'))
    education = soup.find('div', dict(id=id_prefix+'pnlHabilitacoes'))
    current_jobs = soup.find('div', dict(id=id_prefix+'pnlCargosDesempenha'))
    jobs = soup.find('div', dict(id=id_prefix+'pnlCargosExercidos'))
    awards = soup.find('div', dict(id=id_prefix+'pnlCondecoracoes'))
    comissions = soup.find('div', dict(id=id_prefix+'pnlComissoes'))
    mandates = soup.find('table', dict(id=id_prefix+'gvTabLegs'))

    if not name:
        return {}

    entry = {'id': id,
             'name': name.text,
             'url': url,
             'scrape_date': datetime.utcnow().isoformat()}
    if short:
        entry['shortname'] = short.text
    if birthdate:
        entry['birthday'] = datetime.strptime(birthdate.text, "%Y-%m-%d").date()
    if party:
        entry['party'] = party.text

    entry['education'] = []
    if education:
        #TODO: break educations string into multiple entries, ';' is the separator
        #TODO: these blocks are repeated and should be made into functions
        for each in education.findAll('tr')[1:]:
            text = each.find('span').text
            entry['education'].append(text)

    if occupation:
        entry['occupation'] = []
        for each in occupation.findAll('tr')[1:]:
            entry['occupation'].append(each.text)
    if jobs:
        entry['jobs'] = []
        for each in jobs.findAll('tr')[1:]:
            if '\n' in each.text:
                for j in each.text.split('\n'):
                    if j:
                        entry['jobs'].append(j.rstrip(' .;'))
            else:
                entry['jobs'].append(each.text)
    if current_jobs:
        entry['current_jobs'] = []
        for each in current_jobs.findAll('tr')[1:]:
            if '\n' in each.text:
                for j in each.text.split('\n'):
                    if j:
                        entry['current_jobs'].append(j.rstrip(' .;'))
            else:
                entry['current_jobs'].append(each.text.rstrip(' ;.'))
    if comissions:
        entry['commissions'] = []
        for each in comissions.findAll('tr')[1:]:
            entry['commissions'].append(each.text)

    entry['awards'] = []
    if awards:
        for each in awards.findAll('tr')[1:]:
            if '\n' in each.text:
                for j in each.text.split('\n'):
                    if j:
                        entry['awards'].append(j.rstrip(' .;'))
            else:
                entry['awards'].append(each.text.rstrip(' ;.'))
    if mandates:
        entry['mandates'] = []
        for each in mandates.findAll('tr')[1:]:
            leg = each.findAll('td')
            l = leg[0].text
            number, start_date, end_date = parse_legislature(l)

            entry['mandates'].append({'legislature': number,
                                      'start_date': start_date,
                                      'end_date': end_date,
                                      'constituency': leg[3].text,
                                      'party': leg[4].text})

    return entry


def _scrape():
    all_entries = []

    id = 0
    while True:
        print "retrieving id %d" % id
        try:
            entry = parse_deputy(id)
            if entry != {}:
                all_entries.append(entry)
        except:
            print('Was not able to retrieve id %d' % id)
            break
        id += 1

    return all_entries


def scrape(flush_cache=False):
    file_name = "data.dat"
    try:
        file = open(file_name, "r")
        data = pickle.load(file)
        file.close()
    except IOError:
        data = None

    if data is None or flush_cache:
        file = open(file_name, "w")
        data = _scrape()
        pickle.dump(data, file)
        file.close()
    return data
