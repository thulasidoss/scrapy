import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


url = 'https://www.arubanetworks.com/support-services/security-bulletins/'


geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'


options = Options()
options.binary_location = firefox_binary_path
options.add_argument("--headless")  


driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)


driver.get(url)


WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'resource-content')))

soup = BeautifulSoup(driver.page_source, 'html.parser')


driver.quit()

divs = soup.find_all('div', class_='resource-content content-block-txt')

titles = []
dates = []
cve_numbers = []
descriptions = []


for div in divs:
  
    title = div.find('h3').get_text(strip=True)
    titles.append(title)
    
 
    date = div.find('div', class_='date').get_text(strip=True).replace('Updated:', '').strip()
    dates.append(date)
    

    cve_number = div.find('p', class_='cve-number')
    if cve_number:
        cve_number_text = cve_number.get_text(strip=True).replace('CVE Number:', '').strip()
    else:
        cve_number_text = 'N/A'
    cve_numbers.append(cve_number_text)
    
   
    description = div.find('div', class_='block-text').get_text(strip=True)
    descriptions.append(description)


max_length = max(len(titles), len(dates), len(cve_numbers), len(descriptions))

titles.extend([None] * (max_length - len(titles)))
dates.extend([None] * (max_length - len(dates)))
cve_numbers.extend(['N/A'] * (max_length - len(cve_numbers)))
descriptions.extend([None] * (max_length - len(descriptions)))


data = {
    'Title': titles,
    'Date': dates,
    'CVE Number': cve_numbers,
    'Description': descriptions
}

df = pd.DataFrame(data)


df.to_excel('aruba_security_bulletins.xlsx', index=False)

print("Data has been saved to aruba_security_bulletins.xlsx")
