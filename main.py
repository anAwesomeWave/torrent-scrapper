import traceback
import urllib.parse
import sys

import requests
from bs4 import BeautifulSoup

import logging

# simple logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.FileHandler('logger.log'))


def get_all_torrents(cont): # return list of dicts
    arr = []
    for i in cont.find_all('tr'):
        d = dict()


        # for i in [('is_approved','find_all('td', {'class': 'row1 t-ico'})[1]['title']')]
        # TODO: может сработать для всего, кроме is_approved (цикл для всех остальных соответственно, переписать)


        try:
            d['link'] = 'https://rutracker.org/forum/dl.php?t=' + i['data-topic_id']
        except Exception as e:
            logging.error('forum-LINK - ' + traceback.format_exc())
            log.info('forum-LINK - ' + traceback.format_exc())
            d['link'] = None

        # if we can't get link we skip all next info about file
        if d['link'] is None:
            continue


        # approved or not
        try:
            d['is_approved'] = i.find_all('td', {'class': 'row1 t-ico'})[1]['title']  # or 'status'
        except Exception as e:
            logging.error("is_approved-DICT - " + traceback.format_exc())
            log.info("is_approved-DICT - " + traceback.format_exc())
            d['is_approved'] = None

        # forum
        try:
            d['forum'] = i.select('.row1.f-name-col')[0].find('a').string # by css selector
        except Exception as e:
            logging.error('forum-DICT - ' + traceback.format_exc())
            log.info('forum-DICT - ' + traceback.format_exc())
            d['forum'] = None

        try:
            #d['filename'] = i.find('td', {'class': 'row4 med tLeft t-title-col tt'}).find('a').string
            d['filename'] = i.select('.row4.med.tLeft.t-title-col.tt')[0].find('a').string
        except Exception as e:
            logging.error('forum-FILENAME - ' + traceback.format_exc())
            log.info('forum-FILENAME - ' + traceback.format_exc())
            d['filename'] = None

        # author
        try:
            d['author'] = i.select('.row1.u-name-col')[0].find('a').string
        except Exception as e:
            logging.error('forum-AUTHOR - ' + traceback.format_exc())
            log.info('forum-AUTHOR - ' + traceback.format_exc())
            d['author'] = None

        # size TODO: убрать лишнее из строки
        try:
            d['size'] = i.select(".row4.small.nowrap.tor-size")[0].find('a').string
        except Exception as e:
            logging.error('forum-SIZE - ' + traceback.format_exc())
            log.info('forum-SIZE - ' + traceback.format_exc())
            d['size'] = None

        # seeds
        try:
            # d['seeds'] = i.select('.row4.nowrap')[1].find('b').string
            d['seeds'] = i.find('b').string
        except Exception as e:
            logging.error('forum-SEEDS - ' + traceback.format_exc())
            log.info('forum-SEEDS - ' + traceback.format_exc())
            d['seeds'] = None

        # leeches
        try:
            d['leeches'] = i.select('.row4.leechmed.bold')[0].string
        except Exception as e:
            logging.error('forum-LEECHES - ' + traceback.format_exc())
            log.info('forum-LEECHES - ' + traceback.format_exc())
            d['leeches'] = None

        # downloads
        try:
            d['downloads'] = i.select('.row4.small.number-format')[0].string
        except Exception as e:
            logging.error('forum-DOWNLOADS - ' + traceback.format_exc())
            log.info('forum-DOWNLOADS - ' + traceback.format_exc())
            d['downloads'] = None
        # date
        try:
            d['date'] = i.find('p').string
        except Exception as e:
            logging.error('forum-DATE - ' + traceback.format_exc())
            log.info('forum-DATE - ' + traceback.format_exc())
            d['date'] = None
        arr.append(d)
    return arr


def download_file(file, cookies):
    r = requests.get(file['link'], cookies=cookies)
    filename = ""
    for i in file['filename']:
        if not i in '/.\\':
            filename += i
    open(f'./{filename}.torrent', 'wb').write(r.content)


login_url = 'https://rutracker.org/forum/login.php'

# get login and password from rutracker
f = open('keys.txt', 'r')
keys = f.read().split()
f.close()

# body data
values = {
    'login_username': keys[0],
    'login_password': keys[1],
    'login': '%C2%F5%EE%E4'

}

try:
    r = requests.post(login_url, data=values, allow_redirects=False)
except requests.exceptions.ConnectionError:
    log.info('CANNOT LOG-IN: connection error')
    log.info(requests.exceptions.ConnectionError)
    print('CANNOT LOG-IN: connection error')
    sys.exit()

# for c in r.cookies:
#     print(c.name, c.value)
user_input = urllib.parse.quote("peaky blinders 2")  # Percent-encoding

# get all matches from rutracker
# pass cookie to authenticate
user_request = requests.get(f'https://rutracker.org/forum/tracker.php?nm={user_input}', cookies=r.cookies).content

soup = BeautifulSoup(user_request, 'html.parser')  # .prettify()

container = soup.find('div', {"id": "search-results"}).find('tbody')
all_torrents = get_all_torrents(container)  # list of dicts (all torrents)
# name, size, link, date, author, seeds, leeches

# TODO: iterate through all pages
# class bottom_info -> class nav -> class pg-jump-menu -> find_all('a' class pg)
# request к каждой

for i in all_torrents:
    print(i)

torrent_index = int(input())

if torrent_index > 0 and torrent_index < len(all_torrents):
    download_file(all_torrents[torrent_index], r.cookies)

# мб завернуть все в класс и сделать функции
# типа api
# а потом в других скриптах уже пользоваться
