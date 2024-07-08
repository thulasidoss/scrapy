from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'


options = Options()
options.binary_location = firefox_binary_path


gecko_driver_path = r'C:\Users\user01\Documents\scraping\geckodriver.exe'


driver = webdriver.Firefox(service=Service(executable_path=gecko_driver_path), options=options)


driver.get("https://www.amd.com/en/resources/product-security.html")


time.sleep(5)  # Wait for 5 seconds

# Find the select element for changing entries per page
select_element = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.NAME, "DataTables_Table_0_length"))
)

# Scroll the select element into view
driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });", select_element)

# Wait until the select element is visible and interactable
WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.NAME, "DataTables_Table_0_length"))
)

# Select the option with value "100" using JavaScript click to bypass scrolling issues
driver.execute_script("arguments[0].value = '100';", select_element)

# Trigger change event if necessary (depends on how the page handles the dropdown)
driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", select_element)

time.sleep(5)  # Wait for 5 seconds

# scrape the table data
table = driver.find_element(By.ID, "DataTables_Table_0")
rows = table.find_elements(By.TAG_NAME, "tr")


data = []


for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if cells:  # Check if row is not empty (header row check)
        amd_id = cells[0].text.strip()  
        title = cells[1].text.strip()  
        type = cells[2].text.strip()    
        cves = cells[3].text.strip()    
        p_date = cells[4].text.strip()  # Assuming fifth column is Published_date
        u_date = cells[5].text.strip()  # Assuming sixth column is Updated_date
        
       
        data.append({
            "Title": title,
            "CVEs": cves,
            "AMD_ID": amd_id,
            "Type": type,
            "P_date": p_date,
            "U_date": u_date
        })

# Close the browser session
driver.quit()


df = pd.DataFrame(data)


excel_file = "amd_security_data.xlsx"
df.to_excel(excel_file, index=False)

print(f"Scraped data saved to {excel_file}")
