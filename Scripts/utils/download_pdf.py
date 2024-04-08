import csv
import os
import requests
import tools
import sys
sys.path.append('/pfs/data5/home/kit/stud/uqqww/DataSetPopScience')
sys.path.append('/pfs/data5/home/kit/stud/uqqww/DataSetPopScience/Scripts')


root_path = '../../ParallelCorpus'
name = 'ScienceDaily'
folder_path = os.path.join(root_path, name)

csv_path = os.path.join(folder_path, 'store')

pdf_path = os.path.join(folder_path, 'pdf_files')

os.makedirs(pdf_path, exist_ok= True)

def solver(budget):
    files = os.listdir(csv_path)
    csv_files = [file for file in files if file.endswith('.csv') and 'Enviro' not in file and 'Health' not in file]
    # csv_files = [file for file in files if file.endswith('.csv') and 'Health' in file]

    for csv_file in csv_files:
        index = 0

        csv_file_path = os.path.join(csv_path, csv_file)
        print(f'Entering {csv_file_path} downloading')

        with open(csv_file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            rows = list(csv_reader)
        #
        if 'Enviro' in csv_file:
            rows = rows[3456 : -1]
            index = 0

        if 'Tech' in csv_file:
            rows = rows[2374: -1]
            index = 0

        if 'Health' in csv_file:
            rows = rows[2752: -1]
            index = 0


        for row in rows:
            try:
                print(f'entering {index} out of {len(rows)}')
                download_pdf(row, budget=budget, index=index)
                index += 1
            except:
                index += 1
                continue

def download_pdf(row, budget, index):
    if budget <= 0:
        return
    doi = row['reference']
    topic = row['topic']
    id = row['id']

    pdf_name = f'{topic}_{id}.pdf'

    pdf_exist = int(row['pdf_exist'])

    pdf_store_file = os.path.join(pdf_path, pdf_name)

    if pdf_exist == 0:
        # try nature
        nature_paper_site = 'https://www.nature.com/articles/'
        ad_hoc_doi = doi.split('/')[-1]
        response = requests.get(nature_paper_site + ad_hoc_doi + '.pdf')

        if response.status_code == 200:
            with open(pdf_store_file, 'wb') as file:
                file.write(response.content)
            pdf_exist = 1
            row['pdf_exist'] = 1

    # try springer
    if pdf_exist == 0:
        springer_paper_site = 'https://link.springer.com/content/pdf/'
        response = requests.get(springer_paper_site + doi + '.pdf')
        if response.status_code == 200:
            with open(pdf_store_file, 'wb') as file:
                file.write(response.content)
            pdf_exist = 1
            row['pdf_exist'] = 1

    # try google scholar
    if pdf_exist == 0:
        serpa_url = tools.serpapi_search(doi)
        if serpa_url is not None:
            tools.download_pdf(serpa_url, pdf_path, pdf_name)
            pdf_exist = 1
            row['pdf_exist'] = 1
            budget -= 1

    if(pdf_exist == 1):
        print(f'{index} download success')
    else:
        print(f'{index} download failed')

import pandas as pd

def modify_pdf_exist_manually():
    files = os.listdir(csv_path)
    csv_files = [file for file in files if file.endswith('.csv') and 'Life_science_pls' in file]

    df = pd.read_csv(csv_files[0])

    folder_path = pdf_path

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            file_id = file_name.split('_')[-1].split('.')[0]
            df.loc[df['id'] == int(file_id), 'pdf_exist'] = 1

    df.to_csv('your_csv_file_updated.csv', index=False)


if __name__ == "__main__":
    budget = 10000
    solver(budget)






