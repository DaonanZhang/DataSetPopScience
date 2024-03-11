import random

import requests
from bs4 import BeautifulSoup as bs, NavigableString
from selenium import webdriver
import time
import os
from selenium.webdriver.common.by import By
import csv
import re
import sys
from Scripts.utils import tools

sys.path.append('/pfs/data5/home/kit/stud/uqqww/DataSetPopScience')
sys.path.append('/pfs/data5/home/kit/stud/uqqww/DataSetPopScience/Scripts')

root_path = '../../ParallelCorpus'
name = 'ScienceNet.CN'

# PLAN: 2100 articles

folder_name = os.path.join(root_path, name)
href_folder = os.path.join(folder_name, 'href')
# tools.make_dir(root_path, name)
pdf_folder_path = os.path.join(folder_name, 'pdf_files')
# tools.make_dir(folder_name, 'pdf_files')
os.makedirs(href_folder, exist_ok=True)

topics = {
    'Medical': '1',
    'Life_science': '2',
    'Earth_science': '3',
    'Chemical': '4',
    'Industry': '5',
    'Information_science': '6',
    'Mathematics': '7',
}

# # debug mode
# topics = {'Medical': '1',}
# hrefs = ['https://paper.sciencenet.cn/htmlpaper/2024/2/20242614361725895218.shtm']

# unique_id = 0
#
# # create files to store hrefs
# for topic, id in topics.items():
#
#     pdf_topic_folder_path = os.path.join(pdf_folder_path,  topic)
#     tools.make_dir(pdf_folder_path,  topic)
#
#     unique_id = 0
#
#     main_page = f'https://paper.sciencenet.cn/paper/fieldlist.aspx?id={id}'
#     hrefs = []
#
#     href_csv = href_folder + f'/hrefs_{topic}.csv'
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
#     driver.get(main_page)
#
#     # for load more articles / to get hrefs
#     # each page have 30 articles
#
#     total_pages = 30
#     for page_number in range(1, total_pages):
#         soup = bs(driver.page_source, 'lxml')
#         tr_tags = soup.find_all('tr')
#         for tr in tr_tags:
#             a_tag = tr.find('a')
#             if a_tag and 'href' in a_tag.attrs and 'fieldlist' not in a_tag['href']:
#                 href = 'https://paper.sciencenet.cn' + a_tag['href']
#                 if href not in hrefs:
#                     hrefs.append(href)
#
#         # go to the next page
#         # roll down to the bottom
#         if page_number + 1 != total_pages:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             input_element = driver.find_element(By.NAME, 'AspNetPager1_input')
#             input_element.clear()
#             input_element.send_keys(f'{page_number}')
#             submit_button = driver.find_element(By.NAME, 'AspNetPager1')
#             submit_button.click()
#             time.sleep(4)
#
#     with open(href_csv, 'w') as f:
#         for href in hrefs:
#             f.write(href + '\n')
#
#     print(f'{topic} hrefs Load done')

# checking the domain of the source web page for each href in hrefs and write to csv
# picking 2-3 most popular domain to write scirpt ad hoc

for topic, id in topics.items():
    # for each topic
    hrefs = []
    for file_name in os.listdir(href_folder):
        file_name = os.path.join(href_folder, file_name)
        # load hrefs from csv with this topic in the folder
        if topic in file_name:
            with open(file_name, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    hrefs.append(row)

    print(f'{topic} {len(hrefs)} hrefs loaded')

    unique_id = 0
    doi = ''

    # variables for break-point
    break_point = 0
    break_point_id = 0
    hrefs = hrefs[break_point: -1]
    unique_id += break_point_id

    for index_hrefs, urls in enumerate(hrefs):
        try:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(urls, headers=hdr)
            source = r.content
            soup = bs(source, 'lxml')
            div_tag = soup.find('div', id='content1')
            p_tag = div_tag.find_all('p')
            pls_full_text = ''
            pls_summaries = ''
            reference = ''

            title = div_tag.find_all('td', class_='style1', align='center')[1].get_text()

            title = re.sub(r"\s+", "", title)

            for index, p in enumerate(p_tag):
                if index != 0 and index != len(p_tag) - 1:
                    for child in p.children:
                        if isinstance(child, NavigableString) and child != '\n':
                            pls_full_text += child

                if index == 1:
                    pls_summaries = p.get_text()

                # also possible appear in the (len - 2)
                if index >= len(p_tag) - 4:
                    reference_tag = p.find('a', href=True, target='_blank')
                    if reference_tag is not None:
                        reference = reference_tag['href']
                        doi = reference.split('/')[-2] + '/' + reference.split('/')[-1]

            # PLS summaries
            pls_full_text = re.sub(r'（来源：[^）]+）', '', pls_full_text)
            # may don't have the reference
            # if exception, don't extract pls_summaries

            clean_abstract = tools.fromDOItoAbstract(doi)
            authors_info, journey = tools.fromDOItoAuthorINFO(doi)

        except Exception as e:
            # print(f'Error in {index_hrefs + break_point} out of {len(hrefs) + break_point}')
            print(e)
            break
            # continue

        # if reference and text exist
        if clean_abstract and pls_summaries and len(authors_info) != 0:
            pdf_exist = 0

            # pdf_name = os.path.join(pdf_topic_folder_path, f'{topic}_{unique_id}.pdf')

            # # try nature
            # nature_paper_site = 'https://www.nature.com/articles/'
            # ad_hoc_doi = doi.split('/')[-1]
            # response = requests.get(nature_paper_site + ad_hoc_doi + '.pdf')

            # if response.status_code == 200:
            #     with open(pdf_name, 'wb') as file:
            #         file.write(response.content)
            #         pdf_exist = 1

            # # try springer
            # if pdf_exist == 0:
            #     springer_paper_site = 'https://link.springer.com/content/pdf/'
            #     response = requests.get(springer_paper_site + doi + '.pdf')
            #     if response.status_code == 200:
            #         with open(pdf_name, 'wb') as file:
            #             file.write(response.content)
            #             pdf_exist = 1

            # # try google scholar
            # try:
            #     if pdf_exist == 0:
            #         serpa_url = tools.serpapi_search(doi)
            #         if serpa_url is not None:
            #             tools.download_pdf(serpa_url, pdf_folder_path, f'{topic}_{unique_id}.csv')
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
            #     print(f'current index is {index + break_point} out of {len(hrefs) + break_point}')

            tools.saveFile(topic=topic, title=title, pls=pls_summaries, article_full_text=pls_full_text,
                           reference=doi, root_path=root_path, name=name,
                           authors_info=authors_info, journey=journey,
                           abstract=clean_abstract, pdf_exist=pdf_exist, unique_id=unique_id, )
            print(f'{unique_id}. file saved')
            unique_id += 1
            print(f'current index is {index_hrefs + break_point} out of {len(hrefs) + break_point}')



