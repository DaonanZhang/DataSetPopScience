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
href_folder = os.path.join(folder_name, 'href')

tools.make_dir(root_path, name)

topics = [
    'health_medicine',
    'mind_brain',
    'living_well',
    'computers_math',
    'matter_energy',
    'space_time',
    'plants_animals',
    'earth_climate',
    'fossils_ruins',
    'science_society',
    'business_industry',
    'education_learning'
]

# for test
# topics = ['health_medicine']
# hrefs = ['https://www.sciencedaily.com/releases/2024/01/240108153132.htm,',
#          'https://www.sciencedaily.com/releases/2024/01/240117143935.htm']

# create files to store hrefs
for topic in topics:
    hrefs = []
    href_csv = href_folder + f'/hrefs_{topic}.csv'
    if not os.path.exists(href_csv):
        with open(href_csv, 'w') as csv_file:
            pass
    else:
        with open(href_csv, 'r') as f:
            hrefs = f.read().splitlines()

    # for load more articles
    options = webdriver.ChromeOptions()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = webdriver.Chrome()
    driver.get(f"https://www.sciencedaily.com/news/{topic}/")
    time.sleep(2)

    # accept cookies
    try:
        driver.find_element(By.CLASS_NAME, "sc-qRumB.bcoUVc.amc-focus-first").click()
    except:
        continue


    # load how many times more
    # each time load 5 articles: estimation
    # TODO: no more contents after 10 times load more
    for i in range(100):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1500);")
        driver.find_element(By.ID,'load_more_stories').click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1500);")
        time.sleep(2)


    soup = bs(driver.page_source, 'lxml')
    link_elements = soup.find_all('h3', class_='latest-head')

    for element in link_elements:
        href = element.find('a')['href']
        if 'https://www.sciencedaily.com/' not in href:
            href = 'https://www.sciencedaily.com' + href
        if href not in hrefs:
            hrefs.append(href)

    with open(href_csv, 'w') as f:
        for href in hrefs:
            f.write(href + '\n')
    print('Load hrefs done')


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
            story_text_tag = soup.find('div', id='story_text')
            story_text = story_text_tag.get_text() if story_text_tag else ''
            # full text pls
            pls_summaries = story_text
            a_tag = soup.find('ol', class_='journal').find_all('a')

            if len(a_tag) == 1:
                reference += a_tag[0].get_text()
                print(reference)
        except:
            continue
        # clean_abstract = tools.fromDOItoAbstract(reference)
        # if reference exist
        if (reference != '' and pls_summaries != ''):
            clean_abstract = tools.fromDOItoAbstract(reference)
            # check if clean_abstract is empty
            if clean_abstract != '':
                tools.saveFile(topic, pls_summaries, reference, root_path, name, clean_abstract)

    driver.close()