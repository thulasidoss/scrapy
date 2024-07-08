import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL of the Android Security Bulletin page
url = 'https://source.android.com/docs/security/bulletin/2024-06-01'

# Paths to geckodriver and Firefox binary
geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Configure Firefox options
options = Options()
options.binary_location = firefox_binary_path

# Initialize Firefox WebDriver
driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)
driver.get(url)

try:
    # Wait for the tbody elements to be present
    wait = WebDriverWait(driver, 10)
    tbody_elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'tbody')))
    
    data_rows = []

    for tbody in tbody_elements:
        th_elements = tbody.find_elements(By.TAG_NAME, 'th')
        has_cve_header = any(th.text.strip() == 'CVE' for th in th_elements)

        if has_cve_header:
            tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

            for tr in tr_elements:
                try:
                    # Find all td elements within tr
                    td_elements = tr.find_elements(By.TAG_NAME, 'td')

                    # Extract text from each td element
                    row_data = [td.text.strip() for td in td_elements]
                    
                    # Append row data to list of data rows
                    data_rows.append(row_data)

                except NoSuchElementException:
                    # Handle case where td elements are not found in a row
                    print("No data found in this row")

    # Create a DataFrame
    df = pd.DataFrame(data_rows, columns=['CVE', 'References', 'Type', 'Severity', 'Updated AOSP versions'])

    # Save DataFrame to Excel
    output_file = 'android.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

finally:
    # Close the browser
    driver.quit()
