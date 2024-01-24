# BSE_API

**Disclaimer:** BSE website restricted the download of the ZIP file using Python scripts. As a workaround, I used Selenium to essentially scrape the file.

But I have included correct code to depict the how to use `requests` had bse not put the restrictions.
The support for fetching the last 50 days' data uses `requests`, which is disallowed. `requests` auto-fills required metadata that occurs between a browser and a client. However, the headers field might not match what BSE requires, and determining the correct configuration for websites with complete freedom to set configurations and send arbitrary status codes is a meticulous process. Under time constraints, I decided to fetch the present date's CSV file using Selenium.

## Installation

Use the following code to install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

* ## extract_csv file
  * Since there can be a discrepancy in the uploading schedule of BSE, if the URL provided doesn't have the present date's equity list, please change the file name in the download_and_extract_zip function from '
    ```python 
    EQ%s_CSV.ZIP' % (datetime.utcnow().strftime('%d%m%y'))
    ```
    to whatever date is on the URL [https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx], for example, 'EQ240124_CSV.ZIP'.
  * Change the path (in the ZipFile parameter) to the correct directory corresponding to your system.
* ## Database file
  * Input the correct field for connection with the database.
* ## Setting up and running
  After setting up correctly, run the files in the following order:
  ```bash
  python database.py  # to set up tables in the database
  python extract_csv.py  # to fetch CSV
  ```
* ## Running API
  ```bash
  uvicorn app.main:app --reload
  ```
  * The first "app" is the folder name.
  * The second "app" is the FastAPI instance.
