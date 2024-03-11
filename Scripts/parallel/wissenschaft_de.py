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

# PLAN: 3000 articles

root_path = '../../ParallelCorpus'
name = 'Wissenschaft_DE'

folder_name = os.path.join(root_path, name)
href_folder = os.path.join(folder_name, 'href')
pdf_folder_path = os.path.join(folder_name, 'pdf_files')

tools.make_dir(root_path, name)
tools.make_dir(folder_name, 'pdf_files')

#
topics = [
    'astronomie-physik',
    'technik-digitales',
    'gesundheit-medizin',
    'erde-umwelt',
    'geschichte-archaeologie',
    'gesellschaft-psychologie'
]

topics_translation = [
    'astronomy-physics',
    'technology-digital',
    'health-medicine',
    'earth-environment',
    'history-archaeology',
    'society-psychology'
]

# for test
# topics = ['astronomie-physik']
# hrefs = ['https://www.wissenschaft.de/gesellschaft-psychologie/wieso-live-musik-uns-emotional-staerker-beruehrt-als-tonaufnahmen/']

# create files to store hrefs
# for topic in topics:
#     #
#     pdf_topic_folder_path = os.path.join(pdf_folder_path,  topic)
#     tools.make_dir(pdf_folder_path,  topic)
#     #
#     hrefs = []
#     os.makedirs(href_folder, exist_ok=True)
#
#     href_csv = os.path.join(href_folder, f'/hrefs_{topic}.csv')
#
#     if not os.path.exists(href_csv):
#         with open(href_csv, 'w') as csv_file:
#             pass
#     else:
#         with open(href_csv, 'r') as f:
#             hrefs = f.read().splitlines()
#
#     # for load more articles
#     options = webdriver.ChromeOptions()
#     options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
#     driver = webdriver.Chrome()
#     driver.get(f"https://www.wissenschaft.de/nachrichten-themen/{topic}/")
#
#
#
#     try:
#         # accept cookies
#         wait = WebDriverWait(driver, 5)
#         iframe = wait.until(EC.presence_of_element_located((By.ID, "sp_message_iframe_966577")))
#         driver.switch_to.frame(iframe)
#         button = driver.find_element(By.XPATH, "//button[@title='Zustimmen']")
#         button.click()
#         driver.switch_to.default_content()
#     except:
#         continue
#
#     driver.maximize_window()
#
#
#     max_load = 140
#
#     for i in range(max_load):
#         try:
#             if i == 0 or 1:
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 2000);")
#                 time.sleep(2)
#             else:
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(2)
#             try:
#                 driver.find_element(By.XPATH, "//nav[@class='herald-pagination herald-load-more']/a").click()
#             except:
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 driver.find_element(By.XPATH, "//nav[@class='herald-pagination herald-load-more']/a").click()
#             print(f'load {i} done page')
#         except:
#             break
#
#     link_elements = driver.find_elements(By.XPATH, "//h2[@class='entry-title h3' and not(.//img)]/a")
#
#     for element in link_elements:
#         href = element.get_attribute('href')
#         if href not in hrefs:
#             hrefs.append(href)
#
#     with open(href_csv, 'w') as f:
#         for href in hrefs:
#             f.write(href + '\n')
#     print('Load hrefs done')

for topic_index, topic in enumerate(topics):
    hrefs = []
    translated_topic = topics_translation[topic_index]
    href_csv = os.path.join(href_folder, f'/hrefs_{topic}.csv')

    for file_name in os.listdir(href_folder):
        file_name = os.path.join(href_folder, file_name)
        # load hrefs from csv with this topic in the folder
        if topic in file_name:
            with open(file_name, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    hrefs.append(row)

    print(f'{translated_topic} {len(hrefs)} hrefs loaded')



    unique_id = 0
    break_point = 0
    break_point_id = 0
    hrefs = hrefs[break_point: -1]
    unique_id += break_point_id


    # checking the domain of the source web page for each href in hrefs and write to csv
    # picking 2-3 most popular domain to write scirpt ad hoc

    for index, urls in enumerate(hrefs):
        try:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(urls, headers=hdr)
            source = r.content
            soup = bs(source, 'lxml')
            p_tags = soup.find('div', class_='col-lg-12 col-md-12 col-sm-12').find_all('p')
            # pls_summaries = p_tags[0].get_text(strip=True)
            # [0:-2] to remove the last report informations: Author: xxx
            pls_full_text = '\n'.join([p.get_text(strip=True) for p in p_tags[0:-2]])
            pls_summaries = '\n'.join([p.get_text(strip=True) for p in p_tags[0]])

            # may don't have the reference
            # if exception, don't extract pls_summaries
            reference = p_tags[-2].find('a')['href']
            title = soup.find('h1', class_='entry-title h1 rs-speak').get_text()
            reference = reference.split('/')[-2] + '/' + reference.split('/')[-1]

            doi = reference
            clean_abstract = tools.fromDOItoAbstract(doi)
            authors_info, journey = tools.fromDOItoAuthorINFO(doi)

        except:
            print(f'Error in {index} out of {len(hrefs)}')
            continue

        # if reference exist
        if clean_abstract and pls_summaries and len(authors_info) != 0:
            pdf_exist = 0
            # pdf_name = os.path.join(pdf_topic_folder_path, f'{topic}_{unique_id}.csv')
            #
            # # try nature
            # nature_paper_site = 'https://www.nature.com/articles/'
            # ad_hoc_doi = doi.split('/')[-1]
            # response = requests.get(nature_paper_site + ad_hoc_doi + '.pdf')
            #
            # if response.status_code == 200:
            #     with open(pdf_name, 'wb') as file:
            #         file.write(response.content)
            #         pdf_exist = 1
            #
            # # try springer
            # if pdf_exist == 0:
            #     springer_paper_site = 'https://link.springer.com/content/pdf/'
            #     response = requests.get(springer_paper_site + doi + '.pdf')
            #     if response.status_code == 200:
            #         with open(pdf_name, 'wb') as file:
            #             file.write(response.content)
            #             pdf_exist = 1
            #
            # # try google scholar
            # try:
            #     if pdf_exist == 0:
            #         serpa_url = tools.serpapi_search(doi)
            #         if serpa_url is not None:
            #             tools.download_pdf(serpa_url, pdf_topic_folder_path, f'{topic}_{unique_id}.csv')
            #             pdf_exist = 1
            # except:
            #     continue
            # if pdf_exist == 1:
            #     tools.saveFile(topic=topic, title=title, pls=pls_summaries, article_full_text=pls_full_text,
            #                    reference=doi, root_path=root_path, name=name,
            #                    authors_info=authors_info, journey=journey,
            #                    abstract=clean_abstract, pdf_exist=pdf_exist, unique_id=unique_id, )
            #     print(f'{unique_id}. file saved')
            #     unique_id += 1
            #     print(f'current index is {index} out of {len(hrefs)}')
            tools.saveFile(topic=translated_topic, title=title, pls=pls_summaries, article_full_text=pls_full_text,
                           reference=doi, root_path=root_path, name=name,
                           authors_info=authors_info, journey=journey,
                           abstract=clean_abstract, pdf_exist=pdf_exist, unique_id=unique_id, )
            print(f'{unique_id}. file saved')
            unique_id += 1
            print(f'current index is {index + break_point} out of {len(hrefs) + break_point}')

    # driver.close()