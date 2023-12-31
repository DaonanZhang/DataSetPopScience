import requests
from bs4 import BeautifulSoup as bs
from Scripts.utils import tools
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import csv

root_path = '../../LexicalCorpus'
name = 'Frontiers'

csv_file_path = os.path.join(root_path, name, name + '.csv')
folder_name = os.path.join(root_path, name)
tools.make_dir(root_path, name)


# downwards scrolling
js = '''
               let height = 0;
let interval = setInterval(() => {

    if (height === 0 && window.scrollY !== 0) {
        clearInterval(interval);
        return;
    }
    
    window.scrollTo({
        top: height,
        behavior: "smooth"
    });
    height += 500;
}, 500);
    '''


options = webdriver.ChromeOptions()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
driver = webdriver.Chrome()
driver.get("https://kids.frontiersin.org/articles")


# to check if the hrefs exists before:
# load the hrefs from last time

hrefs = []

if not os.path.exists(folder_name + '/hrefs.csv'):
    os.makedirs(folder_name + '/hrefs.csv')
else :
    with open(folder_name + '/hrefs.csv', 'r') as f:
        hrefs = f.read().splitlines()


hrefs = []
for i in range(1):
    driver.execute_script(js)
    time.sleep(8)

    soup = bs(driver.page_source, 'lxml')
    links = soup.find_all('a', class_='article-link')

    for link in links:
        if link.get('href') not in hrefs:
            hrefs.append(f'https://kids.frontiersin.org/{link.get("href")}')


# after loading all the hrefs, save them to the hrefs.csv file
with open(folder_name + '/hrefs.csv', 'a') as f:
    for href in hrefs:
        f.write(href + '\n')


for url in hrefs:
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = bs(response.text, 'lxml')
    count = 0


    raw_content = []
    while True:
        element_id = f"KC{count + 1}"
        element = soup.find('p', {'id':element_id})
        if element:
            raw_content.append(element.get_text())
            count += 1
        else:
            break


    # delete and sperate the term and the definition
    content = []
    for item in raw_content:
        term, definition = item.split(": ↑ ")
        content.append((term, definition))
    #
    # load the content
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for term, definition in content:
            writer.writerow([term, definition])