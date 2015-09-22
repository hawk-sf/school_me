#!/usr/bin/env python

import os
import sys
import errno
import requests
import urllib
import itertools
import re
import argparse    as ap
import logging     as lg
from   logging     import handlers
from   collections import namedtuple, defaultdict
from   bs4         import BeautifulSoup
from   multiprocessing.dummy import Pool as ThreadPool

VIRTUAL_ENV = os.environ['VIRTUAL_ENV']

logger           = lg.getLogger('cde_scrape')
log_stdout       = lg.StreamHandler(sys.stdout)
file_formatter   = lg.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_formatter = lg.Formatter('%(message)s')
log_stdout.setFormatter(stream_formatter)
log_stdout.setLevel(lg.INFO)
logger.addHandler(log_stdout)
logger.setLevel(lg.DEBUG)


def mkdirs(newdir, mode=0775):
    try:
        os.makedirs(newdir, mode)
    except OSError, err:
        # Reraise the error unless it's about an already existing directory
        if err.errno != errno.EEXIST or not os.path.isdir(newdir):
            raise


class CDERecordLayout(object):
    """
    Schema grabber for CDE Downloadable Data Files' Record Layout table pages,
    based off of School Performance Secion pages (API, AYP, and PI)
    """
    def __init__(self, url):
        self.url  = url
        self.resp = requests.get(url)
        self.soup = BeautifulSoup(self.resp.text, "html.parser")
        self.get_field_definitions()

    def __str__(self):
        return "[%s](%s)" % (self.soup.title.string, self.url)

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)

    def get_data_table(self):
        main_content = self.soup.find('div', {'id': 'maincontent'})
        return main_content.table

    def get_field_definitions(self):
        record_table     = self.get_data_table()
        field_rows       = record_table.findAll('tr')
        self.header      = self.get_row_text(field_rows[0])
        self.Definitions = namedtuple('Definitions', self.header)
        self.fields      = []
        for row in field_rows[1:]:
            values = self.get_row_text(row)
            self.fields.append(self.Definitions._make(values))

    def get_row_text(self, row):
        def clean_string(dirty, allow_spaces=False):
            cleaned = dirty.replace('\r', '').replace('\n', '').replace('#', 'num')
            cleaned = '_'.join(cleaned.strip().split()).lower()
            return cleaned

        strings = [s for s in row.stripped_strings]
        if row.findAll('th'):
            return [clean_string(s) for s in strings]
        else:
            number_of_fields   = len(row.findAll('td'))
            description_string = '\n'.join(strings[(number_of_fields-1):])
            fields             = [clean_string(s) for s in strings[:(number_of_fields-1)]]
            fields.append(description_string)
            return fields

    def write_csv(self):
        file_name = self.soup.title.string.split(' - ')[0].strip().replace(' ', '_')
        with open(file_name + '.csv', 'w') as f:
            header = ','.join(self.header) + '\n'
            f.write(header.encode('utf8'))
            for field in self.fields:
                text = ','.join(list(field)).replace('\r', '').replace('\n', ' ')
                text = ' '.join(text.split()) + '\n'
                f.write(text.encode('utf8'))

    def write_class_py(self):
        file_name = self.soup.title.string.split('-')[0].strip().replace(' ', '_')
        spaces    = max([len(f.field_name) for f in self.fields])
        with open(file_name + '.py', 'w') as f:
            class_def = "class " + file_name + "(db.model):" + '\n'
            f.write(class_def.encode('utf8'))
            for field in self.fields:
                name   = field.field_name.ljust(spaces, ' ')
                column = 'db.Column(db.String(%s))' % field.width
                text   = ' '.join(['   ', name, '=', column])  + '\n'
                f.write(text.encode('utf8'))


def flatten(list_of_lists):
    # Returns a flat list, from a list of iterables
    return itertools.chain.from_iterable(list_of_lists)


class CDEDownloadableFilesBase(object):
    """
    Base class for subclassing CDE downloadable data page scrapers.
    Scrapes CDE Downloadable Data page for Recod Layout links and Data File
    download links. Subclasses need to implement link scraping.
    """

    def __init__(self, url):
        self.url   = url
        self.resp  = requests.get(url)
        self.soup  = BeautifulSoup(self.resp.text, "html.parser")
        logger.info("Scraping: %s", self.soup.title.string.strip())
        self.get_links()

    def __str__(self):
        return "[%s](%s)" % (self.soup.title.string, self.url)

    def __getitem__(self, key):
        return self.links[key]

    def __iter__(self):
        return iter(self.links)

    def _text_filter_links(self, *text):
        return [l for l in self.soup.findAll('a')
                if all(t in ''.join(flatten(l.strings)) for t in text)]

    def get_links(self):
        raise NotImplementedError()

    def get_schema(self, url):
        return CDERecordLayout(url)

    def download_data_file(self, link):
        link_text = link.text.strip().replace('&', 'and').replace(' ', '_')
        file_name = '-'.join([link_text, os.path.basename(link.url)])
        if 'ftp://' not in link.url:
            response = requests.get(link.url)
            with open(file_name, 'wb') as dl:
                dl.write(response.content)
        else:
            urllib.urlretrieve(link.url, file_name)

    def write_schemas(self, num_threads=10):
        pool = ThreadPool(num_threads)

        def schema_worker(link):
            try:
                layout = self.get_schema(link.url)
                layout.write_csv()
                layout.write_class_py()
            except Exception:
                logger.exception("Error writing schema for %s", link)

        try:
            pool.map(schema_worker, self.links['layout'])
        except Exception, e:
            logger.exception(e)
        pool.close()
        pool.join()

    def download_data(self, num_threads=5):
        api_dir = self.soup.title.string.strip().replace('&', 'and').replace(' ', '_')
        mkdirs(api_dir)
        cwd = os.getcwd()
        os.chdir(api_dir)
        pool = ThreadPool(num_threads)

        def dl_worker(link):
            try:
                self.download_data_file(link)
            except Exception:
                logger.exception("Error downloading %s", link.url)

        pool.map(dl_worker, self.links['download'])
        pool.close()
        pool.join()
        os.chdir(cwd)


class CDESchoolPerformanceFiles(CDEDownloadableFilesBase):
    """
    Scrapes CDE Downloadable Data pages for Recod Layout links and Data File
    download links. Based off of School Performance pages (API, AYP, and PI)
    """

    def __init__(self, url):
        super(CDESchoolPerformanceFiles, self).__init__(url)

    def get_links(self):
        self.Link  = namedtuple('Link', ['text', 'url'])

        def get_layout_links(self):
            url_root = os.path.dirname(self.url)
            for l in self._text_filter_links('Layout'):
                yield self.Link._make([l.string, os.path.join(url_root, l['href'])])
            # layout_links = self._text_filter_links('Layout')
            # return [self.Link._make([l.string, os.path.join(url_root, l['href'])])
            #         for l in layout_links]

        def get_download_links(self):
            for l in self._text_filter_links('- Data File'):
                yield self.Link._make([l.string, l['href']])
            # download_links = self._text_filter_links(' Data File ')
            # return [self.Link._make([l.string, l['href']]) for l in download_links]

        self.links = {
                      'layout':   get_layout_links(self),
                      'download': get_download_links(self)
                     }


class CDEDemographicsFiles(CDEDownloadableFilesBase):
    """
    Scrapes CDE Downloadable Data pages for Recod Layout links and Data File
    download links. Based off of School Demographics pages (EL, ELS, FEP, Grad,
    Grad UC/CSF Reqs, SE, SSD, StACD, SD).
    """
    def __init__(self, url):
        super(CDEDemographicsFiles, self).__init__(url)

    def get_links(self):
        self.Link    = namedtuple('Link', ['years', 'text', 'url'])
        self.links   = {
                        'layout':   [],
                        'download': []
                       }
        record_tables = self.soup.find('div', {'id': 'maincontent'}).findAll('table')
        for table in record_tables:
            year_rows = table.findAll('tr')
            for row in year_rows[1:]:
                try:
                    if 'Staff' in self.soup.title.string[:5]:
                        td_years, td_download, td_structure, td_num_records = row.findAll('td')
                    else:
                        td_years, td_download, td_structure = row.findAll('td')
                    year_range    = '-'.join(re.split(u"\u2013", td_years.text))
                    download_link = td_download.a['href']
                    download_text = td_download.text.split()
                    download_name = download_text[0]
                    download_type = download_text[1][1:-1]
                    download_file = '.'.join([download_name, download_type])
                    download      = self.Link._make([year_range,
                                                     download_file,
                                                     download_link])
                    layout_link   = td_structure.a['href']
                    if '://' not in layout_link:
                        url_root    = os.path.dirname(self.url)
                        layout_link = os.path.join(url_root, layout_link)
                    layout_text   = td_structure.text.strip()
                    layout        = self.Link._make([year_range,
                                                     layout_text,
                                                     layout_link])
                    self.links['download'].append(download)
                    self.links['layout'].append(layout)
                except Exception:
                    logger.exception("Error loading years %s", year_range)

    def download_data_file(self, link):
        file_name = link.text
        if 'ftp://' not in link.url:
            response = requests.get(link.url)
            with open(file_name, 'wb') as dl:
                dl.write(response.content)
        else:
            urllib.urlretrieve(link.url, file_name)


# Aggregate download page links from main CDE downloads page, and process ######

CDE_ROOT      = 'http://www.cde.ca.gov/'
CDE_DOWNLOADS = os.path.join(CDE_ROOT, 'ds', 'dd')


def get_download_link_heading(link):
    return link.findParents('table')[0].find_previous_sibling()


def download_pages():
    def is_download_page(link):
        try:
            return get_download_link_heading(link).name == 'h2'
        except Exception:
            return False

    url   = CDE_DOWNLOADS
    resp  = requests.get(url)
    soup  = BeautifulSoup(resp.text, "html.parser")
    links = soup.findAll('a')
    for l in links:
        if is_download_page(l):
            yield l


def get_download_page_dict():
    downloads = defaultdict(lambda: [])
    Link      = namedtuple('Link', ['title', 'url'])
    for page in download_pages():
        head  = ' '.join(get_download_link_heading(page).string.strip().split()).lower()
        href  = page['href'][1:] if page['href'][0] == '/' else page['href']
        url   = os.path.join(CDE_ROOT, href)
        title = ' '.join(page.string.strip().split()).lower()
        downloads[head].append(Link._make([title, url]))
    return downloads


def main(*heads):
    scraper_picker = {
                      'school performance': CDESchoolPerformanceFiles,
                      'demographics':       CDEDemographicsFiles,
                     }
    download_pages = get_download_page_dict()
    base_dir       = os.path.join(VIRTUAL_ENV, 'data')
    mkdirs(base_dir)
    for head in heads:
        scraper = scraper_picker.get(head, None)
        if scraper:
            head_name = '_'.join(head.split())
            head_dir  = os.path.join(base_dir, head_name)
            mkdirs(head_dir)
            os.chdir(head_dir)
            for page in download_pages[head]:
                try:
                    page_name = '_'.join(page.title.split())
                    page_dir  = os.path.join(head_dir, page_name)
                    mkdirs(page_dir)
                    os.chdir(page_dir)
                    downloadable = scraper(page.url)
                    logger.info("Scraping %s", downloadable.soup.title.string.strip())
                    downloadable.write_schemas()
                    downloadable.download_data(num_threads=1)
                except Exception:
                    logger.exception("Error scraping %s", page.url)
    os.chdir(base_dir)


# Script functionality unfinished


def arg_set_up():
    # Set up argument parsing
    parser = ap.ArgumentParser(description = "Temp")
    parser.add_argument('--perf',
                        dest   = "performance",
                        action = "store_true",
                        help   = "School Performance Records")
    parser.add_argument('--demo',
                        dest   = "demographics",
                        action = "store_true",
                        help   = "School Demographics Records")
    return parser.parse_args()

if __name__ == '__main__':
    args     = arg_set_up()
    LOG_ROOT = os.path.join(VIRTUAL_ENV, 'school', 'tmp')
    try:
        log_file = handlers.RotatingFileHandler(os.path.join(LOG_ROOT, "cde_scrape.log"),
                                                maxBytes    = 1024*1024*10,
                                                backupCount = 2)
        log_file.setFormatter(file_formatter)
        log_file.setLevel(lg.DEBUG)
        logger.addHandler(log_file)
    except Exception:
        logger.exception("Problem loading log file %s:", LOG_ROOT)
    try:
        main()
    except Exception, e:
        logger.exception(e)
