
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.belden.com/support/security-assurance'  # Replace with your actual URL
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Assuming the table structure is consistent, find all rows in the table body
    table = soup.find('table', class_='bdn-table')
    if table:
        rows = table.find_all('tr')

        data = []
        for row in rows:
            cells = row.find_all('td')
            if cells:
                identifier = cells[0].text.strip()
                document_title = cells[1].text.strip()
                version = cells[2].text.strip()
                last_updated = cells[3].text.strip()
                document_link = cells[4].find('a')['href'] if cells[4].find('a') else ''

                data.append({
                    'Identifier': identifier,
                    'Document Title': document_title,
                    'Version': version,
                    'Last Updated': last_updated,
                    'Document Link': document_link
                })

        # Convert the data list into a DataFrame
        df = pd.DataFrame(data)

        # Export DataFrame to Excel
        excel_filename = 'belden_documents.xlsx'
        df.to_excel(excel_filename, index=False)
        print(f"Excel file '{excel_filename}' has been created successfully.")

    else:
        print("Table with class 'bdn-table' not found.")

else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
