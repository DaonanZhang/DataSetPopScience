import os
import csv
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from openai import OpenAI
import openai


def make_dir(root_path, name):
    # Ensure the root path exists
    folder = os.path.join(root_path, name)
    if not os.path.exists(folder):
        os.makedirs(folder)

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