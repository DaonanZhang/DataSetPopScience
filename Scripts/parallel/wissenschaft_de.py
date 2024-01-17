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
from selenium.webdriver.support import expected_conditions as EC



root_path = '../../ParallelCorpus'
name = 'Wissenschaft_DE'

folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)

topics = [
    'astronomie-physik',
    'technik-digitales',
    'gesundheit-medizin',
    'erde-umwelt',
    'geschichte-archaeologie',
    'gesellschaft-psychologie'
]

# for test
# topics = ['astronomie-physik']
# hrefs = ['https://www.wissenschaft.de/gesundheit-medizin/tumore-machen-fettzellen-zu-komplizen/']

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
    driver.get(f"https://www.wissenschaft.de/nachrichten-themen/{topic}/")



    try:
        # accept cookies
        wait = WebDriverWait(driver, 5)
        iframe = wait.until(EC.presence_of_element_located((By.ID, "sp_message_iframe_966577")))
        driver.switch_to.frame(iframe)
        button = driver.find_element(By.XPATH, "//button[@title='Zustimmen']")
        button.click()
        driver.switch_to.default_content()
    except:
        continue

    driver.maximize_window()

    # load how many times more
    max_retries = 4
    current_try = 0
    while current_try < max_retries:
        try:
            for i in range(10):
                if i == 0:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 2000);")
                    time.sleep(2)
                else:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                driver.find_element(By.XPATH,"//nav[@class='herald-pagination herald-load-more']/a").click()
        except:
            current_try += 1


    link_elements = driver.find_elements(By.XPATH, "//h2[@class='entry-title h3' and not(.//img)]/a")

    for element in link_elements:
        href = element.get_attribute('href')
        if href not in hrefs:
            hrefs.append(href)

    with open(folder_name + f'/hrefs_{topic}.csv', 'w') as f:
        for href in hrefs:
            f.write(href + '\n')
    print('Load hrefs done')

    # empty by default
    reference = ''

    # checking the domain of the source web page for each href in hrefs and write to csv
    # picking 2-3 most popular domain to write scirpt ad hoc
    for index, urls in enumerate(hrefs):
        try:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(urls, headers=hdr)
            source = r.content
            soup = bs(source, 'lxml')
            p_tags = soup.find('div', class_='col-lg-12 col-md-12 col-sm-12').find_all('p')
            pls_summaries = p_tags[0].get_text(strip=True)
            pls_summaries = '\n'.join([p.get_text(strip=True) for p in p_tags])
            # may don't have the reference
            # if exception, don't extract pls_summaries
            reference = p_tags[-2].find('a')['href']

        except:
            continue

        doi = reference.split('/')[-2] + '/' + reference.split('/')[-1]
        abstract = tools.fromDOItoAbstract(doi)

        # print(pls_summaries)
        # print(reference)
        # print(abstract)
        # if reference exist
        if (reference != ''):
            pass

    driver.close()