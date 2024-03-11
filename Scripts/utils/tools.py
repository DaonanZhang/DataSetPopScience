import os
import csv
import requests
import re
from bs4 import BeautifulSoup as bs
import numpy as np

from readability import Readability

ARXIV_DB_FILE_PATH = "../data/arXive_files/"

def make_dir(root_path, name):
    # Ensure the root path exists
    folder = os.path.join(root_path, name)
    if not os.path.exists(folder):
        os.makedirs(folder)

def fk_ari_score(text):
    r = Readability(text)
    return r.flesch_kincaid(), r.ari()

# def gpt_api():
#     # openai.api_key = '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'
#
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#
#     client = OpenAI()
#
#     completion = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system",
#              "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#             {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#         ]
#     )
#
#     print(completion.choices[0].message)

def fromDOItoAbstract(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)

    if response.status_code != 200:
        return ''

    data = response.json()
    rest_api = data.get('message', 'None')

    xml_abstract = rest_api.get('abstract', 'None')
    soup = bs(xml_abstract, 'lxml')
    abstract_text = soup.find_all('jats:p')
    abstract_combined = ' '.join([tag.get_text() for tag in abstract_text])
    clean_abstract = re.sub(r'\s+', ' ', abstract_combined).strip()


    return clean_abstract

import html
def fromDOItoAuthorINFO(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code != 200:
        return ''
    data = response.json()
    rest_api = data.get('message', 'None')
    author_data = rest_api.get('author', 'None')

    authors_info = []
    for author in author_data:
        full_name = f"{author['given']} {author['family']}"
        affiliations = [aff['name'] for aff in author.get('affiliation', [])]
        author_info = f"{full_name}: {', '.join(affiliations)}"
        authors_info.append(author_info)

    journey = rest_api.get('container-title', 'None')
    journey = html.unescape(journey[0])

    return authors_info, journey


def elsvierAPI(doi):
    # usage guidance: https://dev.elsevier.com/documentation/ArticleRetrievalAPI.wadl

    url = f"https://api.elsevier.com/content/article/doi/{doi}"

    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': '3c1170ac03acc7ecaa1e01d9dc1e7107',
    }
    para = { 'view': 'FULL'}
    response = requests.get(url, headers = headers, params=para)

    if response.status_code != 200:
        print('cant find')
        return ''

    json_data = response.json()
    print(json_data)

def natureAPI(doi):

    key = '31dd7b779e94b92c8fa42d9314a06dfa'

    url = f'http://api.springernature.com/openaccess/pam?q=doi:{doi}&api_key={key}'
    response = requests.get(url)






import csv

def saveFile(topic, pls, reference, root_path, name, scientific_text):

    try:
        fk_score, ari_score = fk_ari_score(pls)
    except:
        fk_score = 'None'
        ari_score = 'None'

    column_names = ['pls',  'fk_score', 'ari_score', 'reference', 'abstract/full_text', 'simirality']

    simirality_score = simirality(pls, scientific_text)

    row = {'pls': pls, 'fk_score': fk_score, 'ari_score': ari_score, 'reference': reference, 'abstract/full_text': scientific_text, 'simirality': simirality_score}

    name = os.path.join(name, 'store')
    make_dir(root_path, name)

    pls_path = os.path.join(root_path, name, f'{topic}_pls.csv')
    pls_extist = os.path.exists(pls_path)

    if pls_extist:
        pls_mode = 'a'
    else:
        pls_mode = 'w'

    with open(pls_path, pls_mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        if pls_mode == 'w':
            writer.writeheader()
        writer.writerow(row)

from sentence_transformers import SentenceTransformer
def simirality(pls, scientific):
    model = SentenceTransformer('sentence-transformers/LaBSE')
    pls_encode = model.encode(pls)
    scientific_encode = model.encode(scientific)
    simirality = np.matmul(pls_encode, np.transpose(scientific_encode))
    return simirality

def fromDOIUrltoDOWId(doi_url):
    # Example: doi_url="https://doi.org/10.48550/arXiv.2105.05862"
    pattern = r"arXiv\.(\d+\.\d+)"
    match = re.search(pattern, doi_url)

    if match:
        arxiv_number = match.group(1)
        return arxiv_number
    else:
        return None


import json
def fromDOItoFullTextArxiv(doi):
    # Example DOI: doi= "https://doi.org/10.48550/arXiv.2105.05862"
    arxiv_number = fromDOIUrltoDOWId(doi)
    if arxiv_number is None:
        return

    folder_prefix = arxiv_number[:2]
    folder_path = os.path.join(ARXIV_DB_FILE_PATH, folder_prefix)

    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return None

    raw_text = []
    for filename in os.listdir(folder_path):
        if filename.startswith(f"arXiv_src_{arxiv_number[:4]}"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    data = json.loads(line)
                    paper_id = data.get("paper_id")
                    if paper_id and paper_id == arxiv_number:
                        data = json.loads(line)
                        body_text_entries = data.get("body_text", [])
                        for entry in body_text_entries:
                            text = entry.get("text", "")
                            raw_text.append(text)
    if raw_text:
        text = "\n".join(raw_text)
        text = re.sub(r"\{\{.*?\}\}", "", text)  # remove inline references
        return text
    else:
        return None