import traceback
import urllib.parse
import sys

import requests
from bs4 import BeautifulSoup

from re import sub

import logging

# simple logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.FileHandler('image.log'))


def get_all_torrents(cont): # return list of dicts
    arr = []
    for i in cont.find_all('tr'):
        d = dict()

        # for i in [('is_approved','find_all('td', {'class': 'row1 t-ico'})[1]['title']')]
        # TODO: может сработать для всего, кроме is_approved (цикл для всех остальных соответственно, переписать)
        # approved or not
        try:
            d['is_approved'] = i.find_all('td', {'class': 'row1 t-ico'})[1]['title'] # or 'status'
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

        # filename
        # хочу брать весь текст
        # включая возмодные теги span
        # а потом, все, что в <> удалять с помощью regex возможно или циклом просто
        # sub(r'<[^<>]*>', str)
        # по итогу не пришлось даже)

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
    print(arr)
    return arr



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
    sys.exit()

# for c in r.cookies:
#     print(c.name, c.value)
user_input = urllib.parse.quote("peaky blinders 2")  # Percent-encoding

# get all matches from rutracker
# pass cookie to authenticate
user_request = requests.get(f'https://rutracker.org/forum/tracker.php?nm={user_input}', cookies=r.cookies).content

soup = BeautifulSoup(user_request, 'html.parser')  # .prettify()

container = soup.find('div', {"id": "search-results"}).find('tbody')
all_torrents = get_all_torrents(container)  # list of dicts (all torents)
# name, size, link, date, author, seeds, leechers

# TODO: iterate through all pages
# class bottom_info -> class nav -> class pg-jump-menu -> find_all('a' class pg)
# request к каждой


#print(container.prettify())


# мб завернуть все в класс и сделать функции
# типа api
# а потом в других скриптах уже пользоваться