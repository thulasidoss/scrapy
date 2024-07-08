import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the page you want to scrape
url = 'https://httpd.apache.org/security/vulnerabilities_24.html'

# Send a HTTP request to the URL
response = requests.get(url)
response.raise_for_status()  # This will raise an exception if the HTTP request returned an unsuccessful status code

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the div with the specific ID
div_id = 'apcontents'  # Replace 'yourDivId' with the actual ID of the div
div_content = soup.find('div', id=div_id)

# List to store the data
data = []

if div_content:
    dt_tags = div_content.find_all('dt')
    if dt_tags:
        for dt in dt_tags:
            text = dt.text.strip()
            parts = text.split(': ', 1)
            if len(parts) == 2:
                severity = parts[0].strip()
                rest = parts[1].strip()
                cve_id_start = rest.find('(')
                cve_id_end = rest.find(')')
                if cve_id_start != -1 and cve_id_end != -1:
                    cve_id = rest[cve_id_start+1:cve_id_end]
                    title = rest[:cve_id_start].strip()
                    data.append([title, cve_id, severity])
                else:
                    data.append([rest, '', severity])
            else:
                print(f"Text format not recognized: {text}")
    else:
        print("No <dt> tags found in the div with ID", div_id)
else:
    print("Div not found.")

# Create a DataFrame and save to Excel
df = pd.DataFrame(data, columns=['Title', 'CVE ID', 'Severity'])
df.to_excel('apache.xlsx', index=False)
