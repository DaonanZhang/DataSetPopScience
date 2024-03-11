import requests
from bs4 import BeautifulSoup as bs
from Scripts.utils import tools
import time
import os
import re
import csv


root_path = '../../ParallelCorpus'
name = 'NatureJP'

folder_name = os.path.join(root_path, name)
href_folder = os.path.join(folder_name, 'href')
tools.make_dir(root_path, name)
pdf_folder_path = os.path.join(folder_name, 'pdf_files')
tools.make_dir(folder_name, 'pdf_files')

hrefs = []
main_page = f'https://www.natureasia.com/ja-jp/research'
href_file_path = os.path.join(href_folder + f'hrefs.csv')


# # debug
# hrefs = ['https://www.natureasia.com/ja-jp/research/highlight/14776']

# done, only need to run once
# r = requests.get(main_page)
# source = r.content
# soup = bs(source, 'lxml')
# h3_tags = soup.find_all('h3', class_='title')
#
# for h3_tag in h3_tags[0:-3]:
#     a_tag = h3_tag.find('a')
#     hrefs.append('https://www.natureasia.com' + a_tag['href'])
# # load hrefs done


if not os.path.exists(href_file_path):
    with open(href_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for row in hrefs:
            writer.writerow([row])
else:
    with open(href_file_path, 'r') as f:
        hrefs = f.read().splitlines()

title = ''
pls_summaries = ''
pls_full_text = ''
reference = ''
unique_id = 0
pdf_exist = 0

break_point = 0
break_point_id = 0
hrefs = hrefs[break_point: -1]
unique_id += break_point_id


for index, href in enumerate(hrefs):
    try:
        time.sleep(3)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(href, headers=hdr)
        source = r.content
        soup = bs(source, 'lxml')

        div_tag = soup.find('div', class_='col-sm-8')
        p_tags = soup.find_all('p', class_=False)

        for id, p_tag in enumerate(p_tags):
            append = p_tag.get_text()
            if id == len(p_tags) - 2:
                append = append[0: -2]
            pls_full_text += append

            if id == 0:
                pls_summaries += append

        pls_full_text = pls_full_text.replace('Nature Japanとつながろう:', '')

        re_reference_in_full_text_1 = r'（https?://[^\s）]+）?'
        re_reference_in_full_text_2 = r'\(https?://[^\s）]+\)?'

        pls_full_text = re.sub(re_reference_in_full_text_1, ' ', pls_full_text)
        pls_full_text = re.sub(re_reference_in_full_text_2, ' ', pls_full_text)

        title = soup.find('h1', class_='title').get_text()

        doi = soup.find('p', class_='doi').get_text().replace('doi:', '')
        authors_info, journey = tools.fromDOItoAuthorINFO(doi)
        clean_abstract = tools.fromDOItoAbstract(doi)
    except:
        continue
    # check if clean_abstract is empty
    if clean_abstract and pls_summaries and len(authors_info) != 0:

        nature_paper_site = 'https://www.nature.com/articles/'
        ad_hoc_doi = doi.split('/')[-1]
        response = requests.get(nature_paper_site + ad_hoc_doi + '.pdf')
        pdf_exist = 0
        pdf_name = os.path.join(pdf_folder_path, f'{unique_id}.pdf')
        if response.status_code == 200:
            with open(pdf_name, 'wb') as file:
                file.write(response.content)
                pdf_exist = 1

        if pdf_exist == 1:
            topic = 'generally'
            tools.saveFile( topic = topic, title = title, pls = pls_summaries, article_full_text = pls_full_text,
                            reference = doi, root_path = root_path, name = name,
                            authors_info = authors_info, journey = journey,
                            abstract = clean_abstract, pdf_exist = pdf_exist, unique_id= unique_id,)
            print(f'{unique_id}. file saved')
            unique_id += 1
            print(f'current index is {index + break_point } out of {len(hrefs) + break_point }')