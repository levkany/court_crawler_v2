"""
    Copyright (c) 2024 levkany
    All rights reserved.

    The source code, including any accompanying documentation
    or files, is the exclusive property of levkany
    ("Owner") and is confidential and proprietary.

    No part of the source code may be reproduced, distributed,
    or transmitted in any form or by any means, including photocopying,
    recording, or other electronic or mechanical methods,
    without the prior written permission of the Owner.

    Unauthorized use, reproduction, or distribution of the source code
    or any portion thereof is strictly prohibited and may result
    in severe civil and criminal penalties.

    For licensing inquiries, please contact levkany.dev@gmail.com
"""


import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import shutil
from requests_ntlm import HttpNtlmAuth
from requests.adapters import HTTPAdapter, Retry
import logging
from utilities import download
from utilities import get_yesterday_date
from utilities import get_links_from_html
from utilities import filter_links_pdffile_only
from utilities import pdf_to_text
from utilities import load_text_file
from extraction import extract_court_name
from extraction import extract_proc_id
from extraction import extract_type
from extraction import extract_judge
from extraction import filter_str
from google_storage import GoogleStorage
from googleapiclient.discovery import build
from logger import logger


abspath = os.path.abspath(os.path.dirname(__file__))
load_dotenv()
os.environ.update({
    'GOOGLE_APPLICATION_CREDENTIALS': str(Path(f'{abspath}/google_service_key.json').absolute())
})

if not os.path.isdir('./downloads'):
    os.mkdir('./downloads')
    
downloads_dir = str(Path('./downloads').absolute())
logger.info('script started')

storage = GoogleStorage(os.getenv("STORAGE"))
service = build("sheets", "v4")
sheet = service.spreadsheets()

session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=2.0,
    status_forcelist=[ 500, 502, 503, 504 ]
)
session.auth = HttpNtlmAuth(os.getenv("S_USER"), os.getenv("S_PASSWORD"))
session.mount('https://', HTTPAdapter(max_retries=retries))


with session as s:
    
    #
    #   download the html index of yesterday
    #

    res = download(
        s, 
        f"{os.getenv('BASE_URL')}/{get_yesterday_date()[1]}/"
    )


    #
    #   extract all links (pdf files) from the html
    #

    links = filter_links_pdffile_only(
        get_links_from_html(res.content.decode().lower())
    )
    
    for link in links:
        try:
            filename = Path(link['href']).name
            res = download(
                s, 
                f"{os.getenv('BASE_URL')}{link['href']}",
                10
            )
            with open(f"{downloads_dir}/{filename}", "wb") as f:
                f.write(res.content)
                f.close()
                
            logger.info(f"{filename} - downloaded and saved!")
            
            # upload the pdf to cloud storage
            storage.upload(open(f"{downloads_dir}/{filename}", "rb"), filename)
            logger.info(f"{filename} uploaded to cloud storage!")

            # convert the pdf to text
            pdf_to_text(str(Path(f"{downloads_dir}/{filename}").absolute()))
            logger.info(f"{filename} converted to text")
            
            # extract data from the text
            textfile_path = str(Path(f"{downloads_dir}/{filename.replace('.pdf', '.txt')}").absolute())
            text = load_text_file(textfile_path)
            
            data = {}
            
            data["proc_id"] = extract_proc_id(text)
            data["court_name"] = extract_court_name(text)
            data["type"] = extract_type(text)
            data["judge"] = extract_judge(text)
            data['date'] = get_yesterday_date()[1]
            data['fileurl'] = f"https://storage.cloud.google.com/{os.getenv('STORAGE')}/{filename}?authuser=1"
            data["text"] = filter_str("".join(text))
            
            # send the data to google sheets
            service.spreadsheets().values().append(
                spreadsheetId=os.getenv("SHEET_ID"), range="data!A1",
                valueInputOption="RAW", body={'values': [list(data.values())]}
            ).execute()
        
        except:
            logger.error("failed to process the pdf")
            
        
    s.close()


#
#   clean up
#

logger.info('CLEAN UP ..')
if os.path.isdir(downloads_dir):
    shutil.rmtree(downloads_dir)

logger.info('script ended')