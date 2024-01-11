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
name = 'ScienceDaily'

folder_name = os.path.join(root_path, name)
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

# create files to store hrefs
for topic in topics:
    hrefs = []
    source_domain = {}
    csv_file_path = os.path.join(root_path, name, name + f'{topic}.csv')

    href_csv = folder_name + f'/hrefs_{topic}.csv'
    if not os.path.exists(href_csv):
        with open(href_csv, 'w') as csv_file:
            pass
    else:
        with open(folder_name + f'/hrefs_{topic}.csv', 'r') as f:
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
    for i in range(2):
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

    with open(folder_name + f'/hrefs_{topic}.csv', 'w') as f:
        for href in hrefs:
            f.write(href + '\n')
    print('Load hrefs done')


    # checking the domain of the source web page for each href in hrefs and write to csv
    # picking 2-3 most popular domain to write scirpt ad hoc
    for index, urls in enumerate(hrefs):
        try:
            print(f'Processing {index}th article with the topic {topic} in total {len(hrefs)} articles')
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
                reference += a_tag[0].get('href')
                print(reference)
        except:
            continue

        # if reference exist
        if (reference != ''):
            # for estimate the source web domain
            response = requests.get(reference ,headers = hdr)
            if response.status_code == 200:
                parsed_url = urlparse(response.url)
                first_level = parsed_url.netloc
                # only extract the abstract from nature
                # if 'nature' in first_level:
                #     source = response.content
                #     soup = bs(source, 'lxml')
                #     scientific_abstract = soup.find('div', class_='c-article-section__content').get_text()

        # TODO: After makeing sure the reference exits,
        #  write the summaries in one file with the unique id as PLS corpus
        #  after extract the abstract from the reference web page:
        #  write the abstract in other file with the same id as Scientific Corpus
        #  Another thing is to check how relevant these two texts are, make set a thresh hold to filter out the irrelevant ones

    #
                if first_level in source_domain:
                    count = source_domain[first_level]
                    source_domain[first_level] = count + 1
                else:
                    source_domain[first_level] = 1
            else:
                continue
    print('Writing Source Domain')
    # after one topic loop
    domain_csv = os.path.join(folder_name, f'source_{topic}_web.csv')
    with open(domain_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Web', 'Count'])
        for key, count in source_domain.items():
            writer.writerow([key, count])

    driver.close()