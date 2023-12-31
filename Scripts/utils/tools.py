import os
import csv
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium import webdriver
import time

def make_dir(root_path, name):
    # Ensure the root path exists
    folder = os.path.join(root_path, name)
    if not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(os.path.join(root_path, name, name + '.csv')):
        csv_file_path = os.path.join(root_path, name, name + '.csv')

        # Create an empty CSV file
        with open(csv_file_path, 'w') as csv_file:
            pass


