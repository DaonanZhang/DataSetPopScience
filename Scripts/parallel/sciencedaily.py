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

root_path = '../../ParallelCorpus'
name = 'ScienceDaily'

folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)

# topics = ['health_medicine', 'mind_brain', 'living_well',
#           'computers_math', 'matter_energy',  'space_time',
#           'plants_animals','earth_climate','fossils_ruins',
#           'science_society','business_industry','education_learning']

topics = ['health_medicine']
hrefs = []


# create files to store hrefs
# for topic in topics:
#
#     csv_file_path = os.path.join(root_path, name, name + f'{topic}.csv')
#
#     href_csv = folder_name + f'/hrefs_{topic}.csv'
#     if not os.path.exists(href_csv):
#         with open(href_csv, 'w') as csv_file:
#             pass
#     else:
#         with open(folder_name + f'/hrefs_{topic}.csv', 'r') as f:
#             hrefs = f.read().splitlines()
#
#
#     href_csv = folder_name + f'/hrefs_{topic}.csv'
#     if not os.path.exists(href_csv):
#         with open(href_csv, 'w') as csv_file:
#             pass
#     else:
#         with open(folder_name + f'/hrefs_{topic}.csv', 'r') as f:
#             hrefs = f.read().splitlines()

    # for load more articles
#     options = webdriver.ChromeOptions()
#     options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
#     driver = webdriver.Chrome()
#     driver.get(f"https://www.sciencedaily.com/news/{topic}/")
#     time.sleep(3)
#
#     # accept cookies
#     try:
#         driver.find_element(By.CLASS_NAME, "sc-qRumB.bcoUVc.amc-focus-first").click()
#     except:
#         pass
#
#
#     # load how many times more
#     for i in range(1):
#         driver.find_element(By.ID,'load_more_stories').click()
#         time.sleep(8)
#
#
#     soup = bs(driver.page_source, 'lxml')
#     link_elements = driver.find_elements(By.CSS_SELECTOR, "div.latest-head a")
#
#
#     for element in link_elements:
#         href = element.get_attribute('href')
#         if href not in hrefs:
#             hrefs.append(href)
#
#     with open(folder_name + f'/hrefs_{topic}.csv', 'w') as f:
#         for href in hrefs:
#             f.write(href + '\n')
#
# #     success load hrefs
#
#: TODO: for each url in hrefs

# example url
url = 'https://www.sciencedaily.com/releases/2023/12/231207161449.htm'

hdr = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=hdr)
source = r.content
soup = bs(source, 'lxml')

head = soup.find('h1', class_='headline').get_text()
summaries = soup.find('dd', id='abstract').get_text()
# empty by default
reference = ''

try:
    reference = soup.find('ol', class_='journal').get_text()
except:
    pass

print(reference)

# if reference exist
if(reference != ''):
    pass


# :TODO: how relevant is the reference to the article, give a score from 0-100 via CHATGPT


