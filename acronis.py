# Import necessary libraries
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration variables
website = 'https://security-advisory.acronis.com/advisories'
geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
output_file = 'acronisdata.xlsx'

options = Options()
options.binary_location = firefox_binary_path

# Initialize a list to store the scraped data
data = []

with webdriver.Firefox(service=Service(geckodriver_path), options=options) as driver:
    # Open the website
    driver.get(website)
    
    # Find all anchor tags with the class name 'search-item'
    search_items = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'search-item')))
    
    for item in search_items:
        # Get the text content of the 'search-item-summary' div
        summary_div = item.find_element(By.CLASS_NAME, 'search-item-summary')
        summary_text = summary_div.text
        
        # Get the text content of the 'el-tag--inactive' div or set to 'nil' if not present
        try:
            cve_div = item.find_element(By.CLASS_NAME, 'el-tag--inactive')
            cve_text = cve_div.text
        except:
            cve_text = 'nil'
        try:
            tooltip_div = item.find_element(By.CLASS_NAME, 'tooltipped')
            tooltip_text = tooltip_div.get_attribute('textContent').strip()  # Strip any leading/trailing whitespace
        except:
            tooltip_text = 'date not found'
        
        # Get the text content of other tag divs excluding those starting with '@'
        severity_texts = []
        for tag_class in ['el-tag--critical', 'el-tag--success', 'el-tag--danger', 'el-tag--warning']:
            tag_divs = item.find_elements(By.CLASS_NAME, tag_class)
            for tag_div in tag_divs:
                text = tag_div.text.strip()
                if not text.startswith('@'):
                    severity_texts.append(text)
        
        severity_text = '; '.join(severity_texts)
        
       
        data.append({
            'Title': summary_text,
            'CVE': cve_text,
            'Severity': severity_text,
            'date': tooltip_text,
            'Description': 'nil' 
        })

# Create a DataFrame from the data and save it to an Excel file
df = pd.DataFrame(data)
df.to_excel(output_file, index=False)

print(f"Data saved to {output_file}")
