import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

url = 'https://psirt.canon/advisory-information/'

geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

options = Options()
options.binary_location = firefox_binary_path
options.headless = True  

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def create_driver():
    return webdriver.Firefox(service=Service(geckodriver_path), options=options)

def extract_links():
    driver = create_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    links = []
    try:
        section_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'box-out__content')))
        for section in section_elements:
            a_tags = [a_tag for a_tag in section.find_elements(By.TAG_NAME, 'a') if re.search(r"CP\d{4}-\d{3,5}", a_tag.text)]
            for a_tag in a_tags:
                link = a_tag.get_attribute('href')
                if link:
                    links.append(link)
    except Exception as e:
        logger.error(f"Error extracting links: {e}")
    finally:
        driver.quit()
    return links

def scrape_details_from_link(link):
    driver = create_driver()
    driver.get(link)
    wait = WebDriverWait(driver, 10)
    h3_text = None
    cve_texts = []
    try:
        h3_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'box-out__title')))
        h3_text = h3_element.text

        cve_texts = re.findall(r"CVE-\d{4}-\d{4,7}", driver.page_source)
    except Exception as e:
        logger.error(f"Error scraping details from link {link}: {e}")
    finally:
        driver.quit()
    return h3_text, cve_texts

if __name__ == "__main__":
    links = extract_links()
    print(links)

    data = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scrape_details_from_link, link): link for link in links}
        for future in as_completed(futures):
            link = futures[future]
            try:
                h3_text, cve_texts = future.result()
                data.append({"Link": link, "Title": h3_text, "CVE": ", ".join(cve_texts)})
                print(f"Link: {link}\nTitle: {h3_text}\nCVE: {cve_texts}\n")
            except Exception as e:
                logger.error(f"Error processing link {link}: {e}")

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    df.to_excel("Canon_Vulnerabilities.xlsx", index=False)
    print("Data has been saved to Canon_Vulnerabilities.xlsx")

