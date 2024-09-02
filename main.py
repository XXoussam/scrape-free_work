import ssl
import gspread
from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Print the SSL version used in the requests
print(ssl.OPENSSL_VERSION)

# Define the Google Sheets API scope
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# Authorize the client with the service account credentials
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "14yRsRVg4ea6mYUPM4cPei1j4OsXIHXS9WP2zk9Y2Z84"
sheet = client.open_by_key(sheet_id)
worksheet = sheet.get_worksheet(0)  # Assumes you're using the first worksheet

# Clear the entire worksheet before inserting new data
worksheet.clear()

# Initialize the data list to store job entries
data = []

# Loop through the pages 1 to 5
for page in range(1, 2):
    url = f"https://www.free-work.com/fr/tech-it/jobs?page={page}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='mb-4 relative rounded-lg max-full bg-white flex flex-col cursor-pointer shadow hover:shadow-md')
        
        for job in job_cards:
            title = job.find('h3').get_text(strip=True)
            company = job.find('div', class_='text-base font-medium truncate w-full').get_text(strip=True)
            location = job.find('span', title=True).get_text(strip=True) if job.find('span', title=True) else 'Not specified'
            description = job.find('div', class_='html-renderer').get_text(strip=True)
            
            # Find the div that contains job types
            job_type_div = job.find('div', class_='tags')
            if job_type_div:
                job_type_tags = job_type_div.find_all('span', class_='tag')
                job_type = ', '.join([tag.text.strip() for tag in job_type_tags if tag.text.strip() in ['Freelance', 'CDI']])
            else:
                job_type = 'Not specified'

            # Find the div that contains requirements
            requirements_div = job.find('div', class_='flex items-center')
            if requirements_div:
                requirements_tags = requirements_div.find_all('span', class_='tag')
                requirements = ', '.join([tag.text.strip() for tag in requirements_tags if tag.text.strip() not in ['Freelance', 'CDI']])
            else:
                requirements = 'Not specified'
            
            data.append({"Job Title": title, "Company": company, "Location": location, "Job Type": job_type, "Requirements": requirements, "Description": description})
    else:
        print(f"Failed to retrieve page {page}. Status code:", response.status_code)

# Convert the list of dictionaries to DataFrame
df = pd.DataFrame(data)
data_list = [df.columns.values.tolist()] + df.values.tolist()
print(data_list)

