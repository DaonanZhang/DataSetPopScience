import os
import csv
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from openai import OpenAI
import openai
import requests
import re
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from readability import Readability
import fasttext
# FASTTEXT_MODEL_PATH = 'F:\\Fasttext_models\\'



def make_dir(root_path, name):
    # Ensure the root path exists
    folder = os.path.join(root_path, name)
    if not os.path.exists(folder):
        os.makedirs(folder)

def fk_ari_score(text):
    r = Readability(text)
    return r.flesch_kincaid(), r.ari()

# def doc_to_vec(doc, model):
#     words = doc.split()
#     word_vecs = [model.get_word_vector(word) for word in words]
#     doc_vec = np.mean(word_vecs, axis=0)
#     return doc_vec
# def similarity(pls, scientific, exo_lang_model, en_lang_model):
#
#     vectorExo = doc_to_vec(pls, exo_lang_model)
#     vectorEn = doc_to_vec(scientific, en_lang_model)
#     similarity = cosine_similarity([vectorExo], [vectorEn])[0][0]
#     return similarity

# from sentence_transformers import SentenceTransformer
# from scipy.spatial import distance
# def similarity(pls, scientific, model):
#     embedding_exo = model.encode(pls)
#     embedding_en = model.encode(scientific)
#     similarity = 1 - distance.cosine(embedding_en, embedding_exo)
#     return similarity

def gpt_power():
    # openai.api_key = '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'

    openai.api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
        ]
    )

    print(completion.choices[0].message)

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

def elsvierAPI(doi, root_path, name):
    url = f"https://api.elsevier.com/content/article/doi/{doi}"
    headers = {
        'X-ELS-APIKey': '3c1170ac03acc7ecaa1e01d9dc1e7107',
        'Accept': 'application/pdf'
    }
    response = requests.get(url, headers = headers)
    filepath = os.path.join(root_path, name + '.pdf')
    with open(filepath, 'wb') as f:
        f.write(response.content)
#

def natureAPI(doi, root_path, name):
    # meta data only
    # key = '31dd7b779e94b92c8fa42d9314a06dfa'
    # url = f'http://api.springernature.com/meta/v2/jats?q=doi:{doi}&api_key={key}'

    url = f'https://link.springer.com/{doi}.pdf'
    response = requests.get(url, stream=True)

    # Replace invalid characters in the filename
    filepath = os.path.join(root_path, name + '.pdf')

    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            for index, chunk in enumerate(response.iter_content(chunk_size=1024000)):
                print(index)
                file.write(chunk)

from pdfminer.high_level import extract_text
def pdfMiner(pdf_path):
    text = extract_text(pdf_path)
    return text

# test
# natureAPI('10.1038/s41586-023-06794-y')
# text = pdfMiner('F:\\DataSetPopScience\\Scripts\\utils\\10.1038_s41586-023-06794-y.pdf')
# print(text)