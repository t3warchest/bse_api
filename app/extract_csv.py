import os
import pandas as pd
from selenium import webdriver
from datetime import datetime, timedelta
import time
from selenium.webdriver.common.by import By
import requests
from zipfile import ZipFile
from io import BytesIO

from . database import create_connection

conn = create_connection()
cursor = conn.cursor()
        

# function to download bhav copy using selenium
def download_and_extract_zip():
    site = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"
    driver = webdriver.Chrome()
    driver.get(site)
    time.sleep(2)
    driver.find_element(By.XPATH,"/html/body/form/div[4]/div/div[2]/div/div[2]/div/div/div[1]/table/tbody/tr/td/table[1]/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/ul/li[1]/a").click()
    time.sleep(5)
    driver.close()
    with ZipFile(os.path.join(os.path.expanduser("~"), "Downloads",'EQ%s_CSV.ZIP' % (datetime.utcnow().strftime('%d%m%y'))), 'r') as zObject: 
        zObject.extractall("./csv_data") 

 
# function to download bhav copy using requests
def download_using_requests(url):
    response = requests.get(url)
    zipfile= ZipFile(BytesIO(response.content))
    zipfile.extractall('./csv_data')


# function to read csv file and store data in pg db
def read_and_store_csv(csv_path):
    df = pd.read_csv(csv_path)

    df = df[['SC_CODE', 'SC_NAME', 'OPEN', 'HIGH', 'LOW', 'CLOSE']]
    
    df['DATE'] = datetime.utcnow().date()
    
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO equity_bhavcopy_data (CODE, NAME, OPEN, HIGH, LOW, CLOSE,DATE)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, tuple(row))

    conn.commit()


# function to fetch last n days data
def n_days_data(n):
    
    end_date = datetime.utcnow().date() - timedelta(days=1)
    start_date = end_date - timedelta(days=n)
    date = start_date
    
    while date <= end_date:
        
        url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ%s_CSV.ZIP" % date.strftime('%d%m%y')
        download_using_requests(url)
        date += timedelta(days=1)


csv_file_path = os.path.join(os.path.expanduser("~"),"Desktop","Hypergro_assignment","app","csv_data",'EQ%s.CSV' % (datetime.utcnow().strftime('%d%m%y')))

# functions in chrnological order to fetch and read zip file:

# download_and_extract_zip()

# read_and_store_csv(csv_file_path)

# n_days_data(50)


