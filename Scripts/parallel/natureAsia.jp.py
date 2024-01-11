import random

import requests
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.wait import WebDriverWait
from Scripts.utils import tools
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import csv
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

root_path = '../../ParallelCorpus'
name = 'NatureJP'

folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)

main_page = f'https://www.natureasia.com/ja-jp/research'
hrefs = []

# csv_file_path = os.path.join(root_path, name + f'hrefs.csv')
#
# if not os.path.exists(csv_file_path):
#     with open(csv_file_path, 'w') as csv_file:
#         pass
# else:
#     with open(csv_file_path, 'r') as f:
#         hrefs = f.read().splitlines()


# r = requests.get(main_page)
# source = r.content
# soup = bs(source, 'lxml')
# h3_tags = soup.find_all('h3', class_='title')
#
# for h3_tag in h3_tags:
#     hrefs.append('https://www.natureasia.com' + h3_tags[0].a['href'])
# load hrefs done

# debug
hrefs.append('https://www.natureasia.com/ja-jp/research/highlight/14759')

title = ''
content = ''
reference = ''

for href in hrefs:
    r = requests.get(href)
    source = r.content
    soup = bs(source, 'lxml')
    
    title = soup.find('h1', class_ = 'title').get_text()

    reference_doi = soup.find('p', class_ = 'doi').get_text().replace('doi:','')
    reference = 'https://dx.doi.org/' + reference_doi

    content = ''