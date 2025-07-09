import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys
import os
import json
from google.oauth2 import service_account


scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']


url = 'https://www.ballou976.com/shop'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'}

r = requests.get(url,headers=headers)

soup = BeautifulSoup(r.content, 'html.parser')

table = soup.find('table',class_='table table-borderless h-100 m-0 o_wsale_context_thumb_cover')
table_rows = table.find_all('tr')
product_list = []

for i in table_rows:
    data = i.find_all('td',class_='oe_product')
    product_list.append(data)

flattened_list = [item for sublist in product_list for item in sublist]
final_data = []
for item in flattened_list:
    title = item.find('h6',class_='o_wsale_products_item_title mb-2').text.strip()
    url = 'https://www.ballou976.com'+ item.find('a',class_='text-primary text-decoration-none').get('href')
    price = item.find('span',class_='oe_currency_value').text
    
    final_data.append({'Title':title,
                       'Link':url,
                       'Price':price})
    

    
df = pd.DataFrame(final_data)
creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
creds_dict = json.loads(creds_json)
creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)

# Authorize with gspread
gc = gspread.authorize(creds)



gauth = GoogleAuth()
drive = GoogleDrive(gauth)
# open a google sheet
gs = gc.open_by_key('YOUR_SHEET_ID')
# select a work sheet from its name
worksheet1 = gs.worksheet('Sheet1')
worksheet1.clear()
set_with_dataframe(worksheet=worksheet1, dataframe=df, include_index=False,
include_column_header=True, resize=True)
print('Google Sheet updated with data')
sys.stdout.flush()
