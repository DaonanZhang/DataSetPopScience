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

root_path = '../../ParallelCorpus'
name = 'ScienceNet.CN'

folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)

topics = {
    # 'Medical': '1',
    'Life': '2',
    'Geo': '3',
    'Chemical': '4',
    'Indutry': '5',
    'Information': '6',
    'Mathematics': '7',
}

# for test
# topics = {'Medical': '1',}

# create files to store hrefs
for topic, id in topics.items():

    main_page = f'https://paper.sciencenet.cn/paper/fieldlist.aspx?id={id}'
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

    options = webdriver.ChromeOptions()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = webdriver.Chrome()
    driver.get(main_page)

    # for load more articles / to get hrefs
    total_pages = 1
    for page_number in range(0, total_pages):
        soup = bs(driver.page_source, 'lxml')
        tr_tags = soup.find_all('tr')
        for tr in tr_tags:
            a_tag = tr.find('a')
            if a_tag and 'href' in a_tag.attrs and 'fieldlist' not in a_tag['href']:
                href = 'https://paper.sciencenet.cn' + a_tag['href']
                if href not in hrefs:
                    hrefs.append(href)

        # go to the next page
        # roll down to the bottom
        if page_number + 1 != total_pages:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            input_element = driver.find_element(By.NAME, 'AspNetPager1_input')
            input_element.clear()
            input_element.send_keys(f'{page_number}')
            submit_button = driver.find_element(By.NAME, 'AspNetPager1')
            submit_button.click()
            time.sleep(4)


    with open(folder_name + f'/hrefs_{topic}.csv', 'w') as f:
        for href in hrefs:
            f.write(href + '\n')

#     print('Load hrefs done')


    # checking the domain of the source web page for each href in hrefs and write to csv
    # picking 2-3 most popular domain to write scirpt ad hoc
    for index, urls in enumerate(hrefs):
        try:
            print(f'Processing {index}th article with the topic {topic} in total {len(hrefs)} articles')
            hdr = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(urls, headers=hdr)
            source = r.content
            soup = bs(source, 'lxml')
            p_tag = soup.find_all('p')
            text = ''
            reference = ''

            for index, p in enumerate(p_tag):
                if index != 0 and index != len(p_tag) - 1:
                    for child in p.children:
                        if isinstance(child, NavigableString) and child != '\n':
                            text += child
                if index == len(p_tag) - 1:
                    reference = p.find('a', href=True, target='_blank')['href']

            text = re.sub(r'（来源：[^）]+）', '', text)
            # may don't have the reference
            # if exception, don't extract pls_summaries
        except:
            continue

        # if reference and text exist
        if (reference != '' and text != ''):
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