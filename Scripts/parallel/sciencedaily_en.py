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
import re

root_path = '../../ParallelCorpus'
name = 'ScienceDaily'

folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)

# topics = [
#     'health_medicine',
#     'mind_brain',
#     'living_well',
#     'computers_math',
#     'matter_energy',
#     'space_time',
#     'plants_animals',
#     'earth_climate',
#     'fossils_ruins',
#     'science_society',
#     'business_industry',
#     'education_learning'
# ]

# for test
topics = ['health_medicine']
hrefs = ['https://www.sciencedaily.com/releases/2024/01/240108153132.htm']

# create files to store hrefs
for topic in topics:
    # hrefs = []
    # source_domain = {}
    # csv_file_path = os.path.join(root_path, name, name + f'{topic}.csv')
    #
    # href_csv = folder_name + f'/hrefs_{topic}.csv'
    # if not os.path.exists(href_csv):
    #     with open(href_csv, 'w') as csv_file:
    #         pass
    # else:
    #     with open(folder_name + f'/hrefs_{topic}.csv', 'r') as f:
    #         hrefs = f.read().splitlines()
    #
    # # for load more articles
    # options = webdriver.ChromeOptions()
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # driver = webdriver.Chrome()
    # driver.get(f"https://www.sciencedaily.com/news/{topic}/")
    # time.sleep(2)
    #
    # # accept cookies
    # try:
    #     driver.find_element(By.CLASS_NAME, "sc-qRumB.bcoUVc.amc-focus-first").click()
    # except:
    #     continue
    #
    #
    # # load how many times more
    # for i in range(2):
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1500);")
    #     driver.find_element(By.ID,'load_more_stories').click()
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1500);")
    #     time.sleep(2)
    #
    #
    # soup = bs(driver.page_source, 'lxml')
    # link_elements = soup.find_all('h3', class_='latest-head')
    #
    # for element in link_elements:
    #     href = element.find('a')['href']
    #     if 'https://www.sciencedaily.com/' not in href:
    #         href = 'https://www.sciencedaily.com' + href
    #     if href not in hrefs:
    #         hrefs.append(href)
    #
    # with open(folder_name + f'/hrefs_{topic}.csv', 'w') as f:
    #     for href in hrefs:
    #         f.write(href + '\n')
    # print('Load hrefs done')


    # checking the domain of the source web page for each href in hrefs and write to csv
    # picking 2-3 most popular domain to write scirpt ad hoc
    for index, urls in enumerate(hrefs):
        try:
            # print(f'Processing {index}th article with the topic {topic} in total {len(hrefs)} articles')
            hdr = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(urls, headers=hdr)
            source = r.content
            soup = bs(source, 'lxml')

            # empty by default
            reference = ''
            # may don't have the reference
            # if exception, don't extract pls_summaries
            pls_summaries = soup.find('dd', id='abstract').get_text()
            a_tag = soup.find('ol', class_='journal').find_all('a')
            if len(a_tag) == 1:
                reference += a_tag[0].get_text()
                print(reference)
        except:
            continue

        # if reference exist
        if (reference != ''):
            doi = reference
            clean_abstract = tools.fromDOItoAbstract(doi)
            # check if clean_abstract is empty
            if clean_abstract != '':
                pass



    # driver.close()