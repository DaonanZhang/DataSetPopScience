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

# topics = [
#     'astronomie-physik',
#     'technik-digitales',
#     'gesundheit-medizin',
#     'erde-umwelt',
#     'geschichte-archaeologie',
#     'gesellschaft-psychologie'
# ]

# for test
topics = ['astronomie-physik']

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


    # # debug
    # hrefs = ['https://www.wissenschaft.de/gesundheit-medizin/tumore-machen-fettzellen-zu-komplizen/']

    # empty by default
    reference = ''

    # checking the domain of the source web page for each href in hrefs and write to csv
    # picking 2-3 most popular domain to write scirpt ad hoc
    for index, urls in enumerate(hrefs):
        try:
            print(f'Processing {index}th article with the topic {topic} in total {len(hrefs)} articles')
            hdr = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(urls, headers=hdr)
            source = r.content
            soup = bs(source, 'lxml')

            p_tags = soup.find('div', class_='col-lg-12 col-md-12 col-sm-12').find_all('p')

            pls_summaries = p_tags[0].get_text(strip=True)

            # may don't have the reference
            # if exception, don't extract pls_summaries
            reference = p_tags[-2].find('a')['href']

        except:
            continue

        print(pls_summaries)
        print(reference)


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
    #
    #     # TODO: After makeing sure the reference exits,
    #     #  write the summaries in one file with the unique id as PLS corpus
    #     #  after extract the abstract from the reference web page:
    #     #  write the abstract in other file with the same id as Scientific Corpus
    #     #  Another thing is to check how relevant these two texts are, make set a thresh hold to filter out the irrelevant ones
    #
    # #
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