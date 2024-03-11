import random

import requests
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from Scripts.utils import tools
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv
from selenium.webdriver.common.by import By
import re
import json

root_path = '../../ParallelCorpus'
name = 'ScienceDaily'


folder_name = os.path.join(root_path, name)
pdf_folder_path = os.path.join(folder_name, 'pdf_files')
href_folder = os.path.join(folder_name, 'href')

tools.make_dir(root_path, name)
tools.make_dir(folder_name, 'pdf_files')

topics = {
    # 'Health': 'health',
    # 'Tech': 'technology',
    'Enviro': 'environment'
    # 'Society': 'society',
}

# debug mode
# topics = {'Health': 'health'}
# hrefs = ['https://www.sciencedaily.com/releases/2024/01/240108153132.htm']

# create files to store hrefs
# for key_word, topic_url in topics.items():
#
#     pdf_topic_folder_path = os.path.join(pdf_folder_path,  key_word)
#     tools.make_dir(pdf_folder_path, key_word)
#
#     json_file = os.path.join(folder_name, 'subtopics', f'subtopics_{topic_url}.json')
#     with open(json_file, 'r') as file:
#         subtopics_url = json.load(file)

    # for index, subtopic in enumerate(subtopics_url):
    #
    #     hrefs = []
    #
    #     href_csv = href_folder + f'/href_{key_word}_{index}.csv'
    #
    #     if not os.path.exists(href_csv):
    #         os.makedirs(href_folder, exist_ok=True)
    #
    #     if not os.path.exists(href_csv):
    #         with open(href_csv, 'w') as csv_file:
    #             pass
    #     else:
    #         with open(href_csv, 'r') as f:
    #             hrefs = f.read().splitlines()
    #
    #     options = webdriver.ChromeOptions()
    #     options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    #     driver = webdriver.Chrome()
    #     driver.get(subtopic)
    #     time.sleep(2)
    #     # accept cookies
    #     try:
    #         driver.find_element(By.CLASS_NAME, "sc-qRumB.bcoUVc.amc-focus-first").click()
    #     except:
    #         continue
    #
    #     # get into headlines tab
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 2300);")
    #     # time.sleep(200)
    #
    #     driver.find_element(By.CSS_SELECTOR, 'li[role="presentation"] a[href="#headlines"]').click()
    #     # load until max_load for each subtopics
    #
    #     max_load = 9
    #
    #     for i in range(1, max_load):
    #
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1800);")
    #         driver.find_element(By.ID,'load_more_stories').click()
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1800);")
    #         time.sleep(20)
    #
    #
    #     soup = bs(driver.page_source, 'lxml')
    #     link_elements = soup.find_all('ul', class_='fa-ul list-padded')
    #
    #     for element in link_elements:
    #         a_tags = element.find_all('a')
    #         for a_tag in a_tags:
    #             href = a_tag['href']
    #             if href not in hrefs:
    #                 hrefs.append(href)
    #
    #     with open(href_csv, 'w') as f:
    #         for href in hrefs:
    #             f.write(href + '\n')
    #     print(f'{subtopic} for {key_word} Load hrefs done')

    # pdf_topic_folder_path = os.path.join(pdf_folder_path,  key_word)
    # tools.make_dir(pdf_folder_path, key_word)
    #
    # href_csv = href_folder + f'/href_{key_word}_{index}.csv'
    #
    # if not os.path.exists(href_csv):
    #     with open(href_csv, 'w') as csv_file:
    #         pass
    # else:
    #     with open(href_csv, 'r') as f:
    #         hrefs = f.read().splitlines()



for key_word, topic_url in topics.items():
    # for each topic
    hrefs = []
    for file_name in os.listdir(href_folder):
        file_name = os.path.join(href_folder, file_name)
        # load hrefs from csv with this topic in the folder
        if key_word in file_name:
            with open(file_name, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    hrefs.append(row)

    print(f'{key_word} {len(hrefs)} hrefs loaded')
    # print(hrefs)
    # break

    unique_id = 0
    break_point = 0
    break_point_id = 0
    hrefs = hrefs[break_point: -1]
    unique_id += break_point_id

    # checking the domain of the source web page for each href in hrefs and write to csv

    for index, urls in enumerate(hrefs):
        try:
            main_page = 'https://www.sciencedaily.com'
            urls = main_page + urls[0]

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
            pls_full_text = story_text_tag.get_text() if story_text_tag else ''

            a_tag = soup.find('ol', class_='journal').find_all('a')
            if len(a_tag) == 1:
                reference += a_tag[0].get_text()

            title = soup.find('h1', class_='headline').get_text()

            doi = reference
            clean_abstract = tools.fromDOItoAbstract(doi)
            authors_info, journey = tools.fromDOItoAuthorINFO(doi)

        except:
            print(f'Error in {index + break_point} out of {len(hrefs) + break_point}')
            continue

        # if reference exist
        if clean_abstract and pls_summaries and len(authors_info) != 0:
            pdf_exist = 0
            # pdf_name = os.path.join(pdf_folder_path, f'{unique_id}.pdf')
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
            # if pdf_exist == 0:
            #     serpa_url = tools.serpapi_search(doi)
            #     if serpa_url is not None:
            #         tools.download_pdf(serpa_url, pdf_topic_folder_path, f'{key_word}_{unique_id}.csv')
            #         pdf_exist = 1

            # if pdf_exist == 1:
            #     tools.saveFile(topic=key_word, title=title, pls=pls_summaries, article_full_text=pls_full_text,
            #                    reference=doi, root_path=root_path, name=name,
            #                    authors_info=authors_info, journey=journey,
            #                    abstract=clean_abstract, pdf_exist=pdf_exist, unique_id=unique_id, )
            #     print(f'{unique_id}. file saved')
            #     unique_id += 1
            #     print(f'current index is {index + break_point} out of {len(hrefs) + break_point}')

            tools.saveFile(topic=key_word, title=title, pls=pls_summaries, article_full_text=pls_full_text,
                           reference=doi, root_path=root_path, name=name,
                           authors_info=authors_info, journey=journey,
                           abstract=clean_abstract, pdf_exist=pdf_exist, unique_id=unique_id, )
            print(f'{unique_id}. file saved')
            unique_id += 1
            print(f'current index is {index + break_point} out of {len(hrefs) + break_point}')
