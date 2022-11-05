import sys

import requests
from bs4 import BeautifulSoup

import logging

# simple logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.FileHandler('image.log'))


#url = 'https://rutracker.org/forum/tracker.php?nm=peaky%20blinders%202'


#headers = {}#'bb-webext': '{"auid":"VGssRNyL7mxf","browser":"chrome-105","proxy":true,"version":"0.9.28"}',
           #'Cookie': 'bb_guid=9jBTHH8Ud4vl; bb_ssl=1; bb_session=0-44811045-5w6kyGfPV9rXTKsXU7Gm; _ym_uid=1658581846128378810; _ym_d=1660744038; _ym_isad=1'}


#r = requests.get(url, headers=headers)


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

soup = BeautifulSoup(r.content, 'html.parser')


for c in r.cookies:
    print(c.name, c.value)
user_input = 'peaky%20blinders%202'  # base64

# get all matches from rutracker
# pass cookie to authenticate
user_request = requests.get(f'https://rutracker.org/forum/tracker.php?nm={user_input}', cookies=r.cookies).content

soup = BeautifulSoup(user_request, 'html.parser') #  .prettify()

container = soup.find('div', {"id": "search-results"})
print(container.prettify())
