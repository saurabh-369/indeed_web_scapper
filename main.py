import os
from random import randint
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
import httpx
import pandas as pd
import time
import re
import json
import logging
from index import close_connection, get_db_connection, get_db_cursor
from send_email import send_email

job_id_list = []
full_job_data_list = []
SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')
dir_path = os.path.dirname(os.path.realpath(__file__))
file_name = os.path.join(dir_path, 'test_log.log')

#logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(file_name)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

## Job Search Parameters
keyword_list = ['software engineer']
location_list = ['California']

def do_logging():
    logger.info("log event")

def get_headers_list():
  response = requests.get(os.getenv('SCRAPEOPS_HEADER_URL') + SCRAPEOPS_API_KEY)
  json_response = response.json()
  return json_response.get('result', [])

def get_random_header(header_list):
  random_index = randint(0, len(header_list) - 1)
  return header_list[random_index]

do_logging()
header_list = get_headers_list()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
}

def get_indeed_search_url(keyword, location, offset=0):
    parameters = {"q": keyword, "l": location, "filter": 0, "start": offset}
    return os.getenv('JOBS_URL') + urlencode(parameters)

def get_scrapeops_url(url):
    payload = {'api_key': SCRAPEOPS_API_KEY, 'url': url}
    proxy_url = os.getenv('SCRAPEOPS_PROXY_URL') + urlencode(payload)
    return proxy_url


for keyword in keyword_list:
    for location in location_list:
        for offset in range(0, 1010, 10): #Update this to pagination
            print("range ::", offset)
            if offset == 10:
                break

            try:
                indeed_jobs_url = get_indeed_search_url(keyword, location, offset)
                response = requests.get(get_scrapeops_url(indeed_jobs_url), headers=get_random_header(header_list))

                print("response.status_code", response.status_code)
                if response.status_code == 200:
                    script_tag  = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
                    if script_tag is not None:
                        json_blob = json.loads(script_tag[0])
                        
                        job_id_list = []
                        jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
                        for index, job in enumerate(jobs_list):
                            if job.get('jobkey') is not None:
                                job_id_list.append(job.get('jobkey'))
                        
                        for job_id in job_id_list:
                            # indeed_jobs_url = get_indeed_search_url(keyword, location, offset)
                            # response = requests.get(get_scrapeops_url(indeed_jobs_url), headers=get_random_header(header_list))
                            indeed_job_url = os.getenv('JOBS_ID_URL') + job_id
                            response = requests.get(get_scrapeops_url(indeed_job_url), headers=get_random_header(header_list))
                            print("job response::", response)
                            if response.status_code == 200:
                                script_tag  = re.findall(r"_initialData=(\{.+?\});", response.text)
                                json_blob = json.loads(script_tag[0])
                                job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]
                        
                                full_job_data_list.append((
                                    # 'jobTitle':
                                    job.get('jobInfoHeaderModel').get('jobTitle') if job.get('jobInfoHeaderModel') is not None else 'Job Title',
                                    #'company': 
                                    job.get('jobInfoHeaderModel').get('companyName') if job.get('jobInfoHeaderModel') is not None else 'Company name',
                                    # 'jobkey': job.get('jobkey') if  job.get('jobkey') is not None else '',
                                    # 'jobDescription': 
                                    job.get('sanitizedJobDescription') if job.get('sanitizedJobDescription') is not None else ' Job Description',
                                ))

                        print("Full job description ::", full_job_data_list)
                        # If response contains less than 10 jobs then stop pagination
                        if len(jobs_list) < 10:
                            break
                    
            except Exception as e:
                print('Error', e)

cur  = get_db_cursor()
print("Cursor ::", cur)
conn = get_db_connection()
print("Connection ::", conn)

for job_desc in full_job_data_list:
    print("Before job_desc ::", job_desc)
    print("After job_desc ::", job_desc)
    cur.execute("insert into master(job_title , company_name, job_description) VALUES(%s, %s, %s)", job_desc)
    conn.commit()

close_connection()

df = pd.DataFrame(full_job_data_list)

df.to_csv(os.getenv('CSV_LOCATION'), index=False, header=True)

if full_job_data_list.len > 0:
    message = "Subject: Jobs!\n\n"
    message += "Found some cool jobs!\n\n"
    
    for job in python_jobs:
        message += f"{json.dumps(job)}\n\n"

    send_email(message)