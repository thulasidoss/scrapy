from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Paths to geckodriver and Firefox binary
geckodriver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Set up Selenium with Firefox in headless mode
options = Options()
options.binary_location = firefox_binary_path
options.headless = True
driver = webdriver.Firefox(options=options)

# URL of the page to scrape
url = "https://advisories.checkpoint.com/advisories/"

# Load the page
driver.get(url)
time.sleep(5)  # Wait for the page to load

# Find the table with the specified ID
table = driver.find_element(By.ID, 'cp_advisory_table_sorter')

# Extract table headers using tag names
headers = [header.text.strip() for header in table.find_elements(By.TAG_NAME, 'th')]
headers.append('Description Link')  # Add a new header for the description link

# Extract table rows using tag names
rows = []
for row in table.find_elements(By.TAG_NAME, 'tr')[1:]:
    cells = row.find_elements(By.TAG_NAME, 'td')
    cells_text = [cell.text.strip() for cell in cells]
    
    # Find the description link if it exists
    try:
        description_link_tag = cells[6].find_element(By.TAG_NAME, 'a')
        description_link = description_link_tag.get_attribute('href') if description_link_tag else ''
    except:
        description_link = ''
    
    # Append the description link as a new column
    cells_text.append(description_link)
    
    rows.append(cells_text)

# Close the Selenium browser
driver.quit()

# Create a DataFrame
df = pd.DataFrame(rows, columns=headers)

# Save the DataFrame to an Excel file
df.to_excel('checkpoint.xlsx', index=False)

