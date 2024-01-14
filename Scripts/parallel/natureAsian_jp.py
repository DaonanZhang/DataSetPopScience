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
import json
import re

root_path = '../../ParallelCorpus'
name = 'NatureJP'

folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)
hrefs = []

main_page = f'https://www.natureasia.com/ja-jp/research'
# debug
# hrefs = ['https://www.natureasia.com/ja-jp/research/highlight/14756']

csv_file_path = os.path.join(root_path, name, name + f'hrefs.csv')

r = requests.get(main_page)
source = r.content
soup = bs(source, 'lxml')
h3_tags = soup.find_all('h3', class_='title')
for h3_tag in h3_tags:
    hrefs.append('https://www.natureasia.com' + h3_tags[0].a['href'])
# load hrefs done

if not os.path.exists(csv_file_path):
    with open(csv_file_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for row in hrefs:
            writer.writerow([row])
else:
    with open(csv_file_path, 'r') as f:
        hrefs = f.read().splitlines()



title = ''
content = ''
reference = ''

for href in hrefs:

    r = requests.get(href)
    source = r.content
    soup = bs(source, 'lxml')

    div_tag = soup.find('div', class_='col-sm-8')
    p_tags = soup.find_all('p', class_= False)

    for p_tag in p_tags:
        content += p_tag.get_text()

    content = content.replace('Nature Japanとつながろう:', '')

    title = soup.find('h1', class_ = 'title').get_text()
    doi = soup.find('p', class_ = 'doi').get_text().replace('doi:','')
    clean_abstract = tools.fromDOItoAbstract(doi)


    # print(content)
    # print(clean_abstract)

    # check if clean_abstract is empty
    if clean_abstract != '':
        pass




