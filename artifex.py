import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the website you want to scrape
url = 'https://artifex.com/security-advisories/'

# Send a GET request to the website
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.content, 'html.parser')

# Find all elements with the class 'child'
elements = soup.find_all(class_='child')

# List to store the data
data = []

# Iterate over each element and extract the relevant information
for element in elements:
    date = element.find(class_='date').get_text(strip=True)
    cve = element.find('p', class_='entry').get_text(strip=True)
    synopsis = element.find('span', class_='entry').get_text(strip=True)
    
    # Append the data to the list
    data.append({
        'Date': date,
        'CVE': cve,
        'Description': synopsis
    })

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_excel('artifex.xlsx', index=False)

