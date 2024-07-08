import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


url = 'https://www.alliedtelesis.com/in/en/support/cybersecurity-vulnerability-statement'

geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'

firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

options = Options()
options.binary_location = firefox_binary_path
driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)
driver.get(url)

try:
    driver.execute_script("window.scrollTo(0, 800);")
    time.sleep(2)

    div_elements = driver.find_elements(By.CSS_SELECTOR, 'div.text-start.container-800.ps-0.block.block__text')

    data = []

    for div_element in div_elements:
        h3_element = div_element.find_elements(By.CSS_SELECTOR, 'h3.pb-2')

        if h3_element:

            h4_e = div_element.find_element(By.TAG_NAME, 'h4')
            h5_e = div_element.find_element(By.TAG_NAME, 'h5')
            p_e = div_element.find_elements(By.TAG_NAME, 'p')

            h4_t = h4_e.text
            h5_t = h5_e.text

            p_t = [p.text for p in p_e]

            cve_ids = []
            for p_text in p_t:
                cve_matches = re.findall(r'CVE-\d{4}-\d{4,7}', p_text)
                if cve_matches:
                    cve_ids.extend(cve_matches)
            
            data.append({
                        'Title': h4_t,
                        'date': h5_t,
                        'CVE IDs': ', '.join(cve_ids) if cve_ids else None,
                        'Description': '\n'.join(p_t)
                        
                    })
         
        df = pd.DataFrame(data)
    
        # Save DataFrame to Excel
        output_file = 'alliedtelesis.xlsx'
        df.to_excel(output_file, index=False)
        
    print(f"Data saved to {output_file}")

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    driver.quit()