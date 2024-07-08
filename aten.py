import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# URL of the security advisory page
url = 'https://www.aten.com/global/en/contact-us/security-advisory/'

# Paths to geckodriver and Firefox binary
geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Configure Firefox options
options = Options()
options.binary_location = firefox_binary_path
options.add_argument("--headless")  # Run in headless mode

# Initialize Firefox WebDriver
driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)
driver.get(url)

# Allow some time for the page to load
time.sleep(3)

# Initialize lists to store data
dates = []
contents = []
cves = []

try:
    # Wait for the elements to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "markets-top-banner"))
    )
    
    # Find all elements with the specified class
    divs = driver.find_elements(By.CLASS_NAME, "markets-top-banner")

    for div in divs:
        try:
            date_tag = div.find_element(By.CLASS_NAME, 'date')
            content_tag = div.find_element(By.TAG_NAME, 'h4')
            cve_tags = content_tag.find_elements(By.CLASS_NAME, 'NoSpan')
            
            date = date_tag.text.strip()
            date = date.replace('[ Release Date: ', '').replace(' ]', '').strip()

            content = content_tag.text.strip().replace(date, "").strip()
            content = content.replace('[ Release Date: ', '').replace(' ]', '').strip()
            
            cve_list = [cve.text.replace('(', '').replace(')', '').strip() for cve in cve_tags]
            cve = ', '.join(cve_list) if cve_list else 'No CVE found'

            dates.append(date)
            contents.append(content)
            cves.append(cve)
        except Exception as e:
            print("Error processing a div:", e)
            continue
finally:
    driver.quit()

# Create a DataFrame from the extracted data
data = {
    'Date': dates,
    'Content': contents,
    'CVE': cves
}

df = pd.DataFrame(data)


df.to_excel('aten_security_advisories.xlsx', index=False)

print("Data has been saved to aten_security_advisories.xlsx")

