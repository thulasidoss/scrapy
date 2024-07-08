from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time


geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

options = Options()
options.binary_location = firefox_binary_path
options.headless = True

url = 'https://advisory.checkmarx.net/'

driver = webdriver.Firefox(options=options)
driver.get(url)
time.sleep(2)

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')

div_class = 'post'
div_contents = soup.find_all('div', class_=div_class)

data = []
for div_content in div_contents:
    ul_ids = div_content.find('ul', class_='ids').text
    ul_ids = ul_ids.replace(' / State: Published','').strip()
    h1 = div_content.find('h1')
    h1_text = h1.text if h1 else 'N/A'  
    p = div_content.find('p')
    p_text = p.text if p else 'N/A'  
    date = div_content.find('label', class_='date')
    date_text = date.text if date else 'N/A' 
    score = div_content.find('div', class_='score-label')
    score_text = score.text if score else 'N/A' 

    data.append({
        'Title': h1_text,
        'description': p_text,
        'date': date_text,
        'CVE': ul_ids,
        'severity': score_text
    })


df = pd.DataFrame(data)
df.to_excel("checkmarx.xlsx", index=False)
