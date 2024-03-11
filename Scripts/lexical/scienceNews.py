import requests
from bs4 import BeautifulSoup as bs
from Scripts.utils import tools
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import csv

root_path = '../../LexicalCorpus'
name = 'ScienceNews'

folder_name = os.path.join(root_path, name)

topics = ['life', 'earth', 'humans', 'space', 'tech']
hrefs = []

for topic in topics:
    csv_file_path = os.path.join(root_path, name, name + f'{topic}.csv')

    href_csv = folder_name + f'/hrefs_{topic}.csv'
    if not os.path.exists(href_csv):
        with open(href_csv, 'w') as csv_file:
            pass
    else:
        with open(folder_name + f'/hrefs_{topic}.csv', 'r') as f:
            hrefs = f.read().splitlines()


    for page_num in range(1,50):
        url = f'https://www.snexplores.org/topic/{topic}/page/{page_num}'
        r = requests.get(url)
        source = r.content
        soup = bs(source, 'lxml')
        h3_tags = soup.find_all('h3', class_ = "post-item-river__title___OLWRU")

        href_new = [h3.find('a')['href'] for h3 in h3_tags if h3.find('a')]
        for h in href_new:
            if h not in hrefs:
                hrefs.append(h)

        # after loading all the hrefs, save them to the hrefs.csv file
        with open(folder_name + f'/hrefs_{topic}.csv', 'a') as f:
            for href in hrefs:
                f.write(href + '\n')
        # go into the next page
        page_num += 1
        try:
            for url in hrefs:
                response = requests.get(url)
                response.encoding = response.apparent_encoding
                soup = bs(response.text, 'lxml')

                power_words_div = soup.find('div', class_='power-words-container')

                p_tags = power_words_div.find_all('p') if power_words_div else []

                content = []
                for p in p_tags:
                    term = p.find('strong').get_text(strip=True)
                    definition = p.get_text(strip=True).replace(term + ': ', '', 1)
                    content.append((term, definition))

                with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for term, definition in content:
                        writer.writerow([term, definition])
        except:
            continue