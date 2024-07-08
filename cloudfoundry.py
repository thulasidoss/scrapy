import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict

url = 'https://www.cloudfoundry.org/foundryblog/security-advisory/'

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
    wait = WebDriverWait(driver, 10)
    links = []  # Use a list to store links in order
    try:
        info_divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'post-tile__info')))
        for info_div in info_divs:
            a_tag = info_div.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            if link:
                links.append(link)
    finally:
        driver.quit()
    return links

def fetch_content(link):
    driver = create_driver()
    driver.get(link)
    wait = WebDriverWait(driver, 10)
    try:
        cve_texts = re.findall(r"CVE-\d{4}-\d{4,7}", driver.page_source)
        
        cve_texts = list(set(cve_texts))
        
        title_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'blog-title')))
        title = title_element.text.strip()
        
        date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.date')))
        date = date_element.text.strip()
        
        return {'Link': link, 'Title': title, 'Date': date, 'CVE_Details': cve_texts}
    finally:
        driver.quit()

def crawl_and_store(links):
    results = OrderedDict()  # Use OrderedDict to preserve insertion order
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_content, link): link for link in links}
        for future in as_completed(futures):
            link = futures[future]
            try:
                result = future.result()
                index = links.index(link) + 1
                results[index] = result
            except Exception as e:
                print(f"Error fetching content for link {link}: {e}")
    
    df = pd.DataFrame(results.values())  # Convert values to list to maintain order
    df.to_excel('scraped_content_with_cve.xlsx', index=False)
    print("Scraped content with CVE details saved to scraped_content_with_cve.xlsx")

# Extract links
extracted_links = extract_links()

# Crawl each link and store content with CVE details in Excel using threading
crawl_and_store(extracted_links)