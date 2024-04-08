
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import os
import pyautogui
import shutil
import threading
import concurrent.futures


pdf_folder = 'F:\DataSetPopScience\ParallelCorpus\ScienceDaily\\pdf_files'
pdf_files = os.listdir(pdf_folder)
out_put_folder = 'F:\DataSetPopScience\ParallelCorpus\ScienceDaily\\\TED_files'
os.makedirs(out_put_folder, exist_ok=True)


def executor_single_pdf(pdf_files, lock):

    thread_id = threading.get_ident()

    out_put_folder =  f'F:\DataSetPopScience\ParallelCorpus\ScienceDaily\\TED_files\\{thread_id}'
    os.makedirs(out_put_folder, exist_ok=True)

    for pdf_file in pdf_files:
        options = webdriver.ChromeOptions()
        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        # driver = webdriver.Chrome()

        download_dir = out_put_folder

        chromeOptions = webdriver.ChromeOptions()

        chromeOptions.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        })

        driver = webdriver.Chrome(chromeOptions)

        Grobid_web = 'http://localhost:8070/'

        driver.get(Grobid_web)

        driver.find_element(By.ID, 'rest').click()

        select_element = driver.find_element(By.ID, 'selectedService')

        select_obj = Select(select_element)

        select_obj.select_by_value('processFulltextDocument')

        checkbox_1 = driver.find_element(By.ID, 'consolidateHeader')
        # checkbox_2 = driver.find_element(By.ID, 'includeRawAffiliations')
        # checkbox_3 = driver.find_element(By.ID, 'consolidateCitations')
        # checkbox_4 = driver.find_element(By.ID, 'includeRawCitations')
        checkbox_5 = driver.find_element(By.ID, 'segmentSentences')

        if not checkbox_1.is_selected():
            checkbox_1.click()
        # if not checkbox_2.is_selected():
        #     checkbox_2.click()
        # if not checkbox_3.is_selected():
        #     checkbox_3.click()
        # if not checkbox_4.is_selected():
        #     checkbox_4.click()
        if not checkbox_5.is_selected():
            checkbox_5.click()

        with lock:
            # ------------------upload pdf file------------------
            pdf_path = os.path.join(pdf_folder, pdf_file)

            upload_button = driver.find_element(By.ID, "btn_block_1")
            upload_button.click()
            time.sleep(4)
            pyautogui.write(pdf_path)
            pyautogui.press('enter')

            # # # optional
            # pyautogui.press('enter')

            # try twice maximum
            interval = 50

            submit_button = driver.find_element(By.ID, "submitRequest")
            submit_button.click()
            time.sleep(2)


        try:
            submit_button = driver.find_element(By.ID, "submitRequest")
            submit_button.click()

            time.sleep(interval)

            btn_download = driver.find_element(By.ID, "btn_download")
            if btn_download:
                btn_download.click()


                print(f'Success')
                time.sleep(2)
                latest_file = max([os.path.join(download_dir, f) for f in os.listdir(download_dir)],
                                  key=os.path.getctime)
                new_file_path = os.path.join(download_dir, f'{pdf_file}.tmp')
                os.rename(latest_file, new_file_path)

        except:
            try:
                # wait for another 30 seconds
                # print(f'another waiting for {interval} seconds')
                time.sleep(interval)
                btn_download = driver.find_element(By.ID, "btn_download")
                if btn_download:
                    btn_download.click()
                    find_element = True

                    print(f'Wait for 30 secs and then Success')
                    time.sleep(2)
                    latest_file = max([os.path.join(download_dir, f) for f in os.listdir(download_dir)],
                                      key=os.path.getctime)
                    new_file_path = os.path.join(download_dir, f'{pdf_file}.tmp')
                    os.rename(latest_file, new_file_path)
            except:
                print(f'Failed')
                continue

        driver.quit()

def rest_pdfs():
    pdf_files = [file for file in os.listdir(pdf_folder) if file.endswith('.pdf')]
    tmp_pdf_files = [file for file in os.listdir(out_put_folder) if file.endswith('.pdf.tmp')]

    unique_pdfs = [pdf for pdf in pdf_files if pdf + '.tmp' not in tmp_pdf_files]

    return unique_pdfs


def process_pdf_files(pdf_files, lock):
    executor_single_pdf(pdf_files, lock)


def delayed_execution(pdf_files, lock):
    process_pdf_files(pdf_files, lock)

def split_list(lst, parts):
    part_size = len(lst) // parts
    split_lists = []

    for i in range(parts):
        start_index = i * part_size
        end_index = start_index + part_size

        if i == parts - 1:
            split_lists.append(lst[start_index:])
        else:
            split_lists.append(lst[start_index:end_index])

    return split_lists



import random
if __name__ == '__main__':
    pdf_files = rest_pdfs()

    length = len(pdf_files)

    global_var = length

    print(f'{length} pdf files')
    #
    pdf_files_chunks = split_list(pdf_files, 2)

    print(len(pdf_files_chunks))

    lock = threading.Lock()

    threads = []
    for chunk in pdf_files_chunks:
        thread = threading.Thread(target=delayed_execution, args=(chunk, lock))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()