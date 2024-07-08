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

# URL to scrape
url = 'https://community.bmc.com/s/group/0F93n000000PlxfCAC/application-security-news?tabset-f2084=1'

# Path to geckodriver and Firefox binary (adjust these paths accordingly)
geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Selenium options
options = Options()
options.binary_location = firefox_binary_path
options.headless = True  # Run in headless mode

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def create_driver():
    return webdriver.Firefox(service=Service(geckodriver_path), options=options)

def extract_links():
    driver = create_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 10)  # Increased wait time to handle slow loading
    links = []
    try:
        # Wait for the elements to be present before extracting links
        h3_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'card__title')))
        for element in h3_elements:
            a_tags = element.find_elements(By.TAG_NAME, 'a')
            for a_tag in a_tags:
                link = a_tag.get_attribute('href')
                links.append(link)
    except Exception as e:
        logger.error(f"Error extracting links: {e}")
    finally:
        driver.quit()
    return links

def scrape_details_from_link(link):
    driver = create_driver()
    driver.get(link)
    wait = WebDriverWait(driver, 10)  # Increased wait time to handle slow loading
    h1_text = ""
    date_time_text = None  # Initialize as None
    try:
        # Wait for the h1 element with the specified class to be present
        h1_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        h1_text = h1_element.text
        
        # Check if the lightning-formatted-date-time element is present
        date_time_elements = driver.find_elements(By.TAG_NAME, 'lightning-formatted-date-time')
        if date_time_elements:
            date_time_text = date_time_elements[0].text
    except NoSuchElementException as e:
        logger.error(f"No such element found while scraping {link}: {e}")
    except StaleElementReferenceException as e:
        logger.warning(f"StaleElementReferenceException encountered while scraping {link}: {e}")
    except Exception as e:
        logger.error(f"Error scraping {link}: {e}")
    finally:
        driver.quit()
    return link, h1_text, date_time_text  # Return link, h1_text, and date_time_text

if __name__ == "__main__":
    links = extract_links()
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scrape_details_from_link, link): link for link in links}
        for future in as_completed(futures):
            link = futures[future]
            try:
                link, h1_text, date_time_text = future.result()
                results.append((link, h1_text, date_time_text))  # Store the results as tuples
            except Exception as e:
                logger.error(f"Error processing {link}: {e}")
    

    df = pd.DataFrame(results, columns=['Link', 'H1 Text', 'Date Time'])
    df.to_excel('bmc.xlsx', index=False)
