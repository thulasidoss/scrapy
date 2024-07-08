import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

url = 'https://docs.bitnami.com/aws/security/'

geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

options = Options()
options.binary_location = firefox_binary_path
options.headless = True  # Run in headless mode

def create_driver():
    return webdriver.Firefox(service=Service(geckodriver_path), options=options)

def extract_links():
    driver = create_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 2)
    links = []
    try:
        tbody_elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'ul')))
        for element in tbody_elements:
            a_tags = element.find_elements(By.TAG_NAME, 'a')
            for a_tag in a_tags:
                link = a_tag.get_attribute('href')
                links.append(link)
    finally:
        driver.quit()
    return links

def process_link(link, index, results, lock):
    local_data = {}
    driver = create_driver()
    driver.get(link)
    wait = WebDriverWait(driver, 2)
    
    retry_count = 0
    while retry_count < 3:
        try:
            headings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.cell.article__heading')))
            if headings:
                local_data['Heading'] = headings[0].text
            break
        except StaleElementReferenceException:
            retry_count += 1
            continue
    
    retry_count = 0
    while retry_count < 3:
        try:
            tables = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.table-wrap')))
            cve_list = []
            for table in tables:
                text = table.text
                cve_ids = re.findall(r'CVE-\d{4}-\d{4,7}', text)
                cve_list.extend(cve_ids)
            if cve_list:
                local_data['CVE'] = ', '.join(cve_list)
            break
        except StaleElementReferenceException:
            retry_count += 1
            continue
    
    driver.quit()
    
    with lock:
        results[index] = local_data

links = extract_links()
results = [None] * len(links)  # Initialize a list to store results in order
lock = Lock()

with ThreadPoolExecutor(max_workers=10) as executor:  # Increase the number of threads
    futures = [executor.submit(process_link, link, index, results, lock) for index, link in enumerate(links)]
    for future in as_completed(futures):
        future.result()  # Ensure all futures are completed

df = pd.DataFrame(results)
df.to_excel('appdynamic.xlsx', index=False)
