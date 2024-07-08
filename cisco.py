from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Path to your geckodriver and Firefox binary
geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Set up the Firefox options
options = Options()
options.binary_location = firefox_binary_path
options.headless = True

# Initialize the WebDriver
driver = webdriver.Firefox(options=options)

try:
    url = "https://sec.cloudapps.cisco.com/security/center/publicationListing.x?product=Cisco&sort=-day_sir#~Vulnerabilities"
    driver.get(url)

    # Wait for the page to load and for the dropdown to be present
    wait = WebDriverWait(driver, 20)
    dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@ng-model='limit']")))

    # Create a Select object
    select = Select(dropdown)

    # Wait for options to be present in the dropdown
    wait.until(lambda driver: len(select.options) > 1)

    # Change the dropdown value to 100
    select.select_by_visible_text('100')

    # Wait for the page to reload
    time.sleep(5)

    # Find the rows in the table with class name "advisoryAlertTable"
    rows = driver.find_elements(By.XPATH, "//tr[@ng-repeat='list in advisoryList']")

    # Extract data from the table
    data = []
    for row in rows:
        try:
            vulnerability_element = row.find_element(By.XPATH, ".//span[@class='advListItem']/a")
            vulnerability = vulnerability_element.text
            link = vulnerability_element.get_attribute('href')
            severity = row.find_element(By.XPATH, ".//td[@class='impactTD']//span[2]").text
            cve = row.find_element(By.XPATH, ".//td[@width='15%']//span").text
            pub_date = row.find_element(By.XPATH, ".//td[@width='15%']/span").text
            version = row.find_element(By.XPATH, ".//td[@width='10%']/span").text
            
            data.append([vulnerability, link, severity, cve, pub_date, version])
        except Exception as e:
            print(f"Error processing row: {e}")

    # Define column names
    columns = ['Vulnerability', 'Link', 'Severity', 'CVE', 'Publication Date', 'Version']

    # Create a DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Save the DataFrame to an Excel file
    output_path = 'cisco_advisories.xlsx'
    df.to_excel(output_path, index=False)

    print(f"Data scraped and saved to {output_path}")

finally:
    # Close the Selenium browser
    driver.quit()
