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
from bs4 import NavigableString
import re
from Scripts.utils import tools

root_path = '../../ParallelCorpus'
name = 'ScienceNet.CN'

FASTTEXT_MODEL_PATH = 'F:\\Fasttext_models\\'

# exo_lang_model = fasttext.load_model(f'{FASTTEXT_MODEL_PATH}cc.ja.300.bin')
# en_lang_model = fasttext.load_model(f'{FASTTEXT_MODEL_PATH}cc.en.300.bin')


folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)


# topics = {
#     'Medical': '1',
#     'Life': '2',
#     'Geo': '3',
#     'Chemical': '4',
#     'Indutry': '5',
#     'Information': '6',
#     'Mathematics': '7',
# }

# for test
topics = {'Medical': '1',}
hrefs = ['https://paper.sciencenet.cn/htmlpaper/2024/1/20241416262834392841.shtm']

# create files to store hrefs
for topic, id in topics.items():
    # main_page = f'https://paper.sciencenet.cn/paper/fieldlist.aspx?id={id}'
    # hrefs = []
    # source_domain = {}
    #
    # csv_file_path = os.path.join(root_path, name, name + f'{topic}.csv')
    # href_csv = folder_name + f'/hrefs_{topic}.csv'
    # if not os.path.exists(href_csv):
    #     with open(href_csv, 'w') as csv_file:
    #         pass
    # else:
    #     with open(folder_name + f'/hrefs_{topic}.csv', 'r') as f:
    #         hrefs = f.read().splitlines()
    #
    # options = webdriver.ChromeOptions()
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # driver = webdriver.Chrome()
    # driver.get(main_page)
    #
    # # for load more articles / to get hrefs
    # total_pages = 1
    # for page_number in range(0, total_pages):
    #     soup = bs(driver.page_source, 'lxml')
    #     tr_tags = soup.find_all('tr')
    #     for tr in tr_tags:
    #         a_tag = tr.find('a')
    #         if a_tag and 'href' in a_tag.attrs and 'fieldlist' not in a_tag['href']:
    #             href = 'https://paper.sciencenet.cn' + a_tag['href']
    #             if href not in hrefs:
    #                 hrefs.append(href)
    #
    #     # go to the next page
    #     # roll down to the bottom
    #     if page_number + 1 != total_pages:
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         input_element = driver.find_element(By.NAME, 'AspNetPager1_input')
    #         input_element.clear()
    #         input_element.send_keys(f'{page_number}')
    #         submit_button = driver.find_element(By.NAME, 'AspNetPager1')
    #         submit_button.click()
    #         time.sleep(4)
    #
    #
    # with open(folder_name + f'/hrefs_{topic}.csv', 'w') as f:
    #     for href in hrefs:
    #         f.write(href + '\n')

#     print('Load hrefs done')
#

    # checking the domain of the source web page for each href in hrefs and write to csv
    # picking 2-3 most popular domain to write scirpt ad hoc
    doi = ''
    for index, urls in enumerate(hrefs):
        try:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(urls, headers=hdr)
            source = r.content
            soup = bs(source, 'lxml')
            div_tag = soup.find('div', id='content1')
            p_tag = div_tag.find_all('p')
            text = ''
            reference = ''

            for index, p in enumerate(p_tag):
                if index != 0 and index != len(p_tag) - 1:
                    for child in p.children:
                        if isinstance(child, NavigableString) and child != '\n':
                            text += child

                if index == len(p_tag) - 1:
                    reference = p.find('a', href=True, target='_blank')['href']
                    doi = reference.split('/')[-2] + '/' + reference.split('/')[-1]


            # PLS summaries
            text = re.sub(r'（来源：[^）]+）', '', text)
                # may don't have the reference
                # if exception, don't extract pls_summaries
        except:
            continue

        print(text)
        print(reference)

        # if reference and text exist
        if (reference != '' and text != ''):
            # scientific abstract
            clean_abstract = tools.fromDOItoAbstract(doi)
            # check if clean_abstract is empty
            if clean_abstract != '':
                pass

    # driver.close()