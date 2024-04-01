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


import datetime
from typing import Tuple
import requests
from time import sleep
from bs4 import BeautifulSoup
import os


def match_word_root(word:str=''):
    if('' == word): return False
    roots = [
        {
            'w_root': ['תבע'],
            'spaces': '2'
        },
        {
            'w_root': ['אשמ', 'אשם'],
            'spaces': '2'
        },
        {
            'w_root': ['בקש', 'משב'],
            'spaces': '2'
        }
    ]

    number_of_matches = 0
    for root in roots:
        number_of_matches = 0
        for inner_root in root['w_root']:
            number_of_matches = 0
            for char in word:
                if(char in inner_root):
                    number_of_matches +=1
                    if(number_of_matches >= 3):
                        return inner_root

    return False


def get_yesterday_date() -> Tuple[str, str]:
    previous_day = datetime.datetime.today() - datetime.timedelta(days=2)
    formatted_date_1 = str(previous_day.year) + '/' + str(previous_day.month) + '/' + str(previous_day.day)
    formatted_date_2 = str(previous_day.year) + '-' + str(previous_day.month) + '-' + str(previous_day.day)
    return (formatted_date_1, formatted_date_2)


def download(session:requests.Session, url:str, wait:int=0):
    if wait > 0:
        sleep(wait)
        
    return session.get(url)


def get_links_from_html(html:str):
    soup = BeautifulSoup(html, features="lxml")
    return soup.findAll('a', href=True)


def filter_links_pdffile_only(links):
    return list(filter(
        lambda link: link['href'].endswith('.pdf'), links
    ))


def pdf_to_text(filepath:str):
    return os.system(f"pdftotext {filepath}")


def load_text_file(filepath:str):
    with open(filepath) as handler:
        data = handler.readlines()
        new_data = []
        for line in data:
            line = str(bytearray(line, 'utf8').decode('utf8'))
            line = line.replace('\n', '')
            if('\n' != line and '' != line and False == line.isdigit()):
                new_data.append(line)
                
        handler.close()
        return new_data


def extract_data(text:list):
    header = []

    # list of items needs to populate
    proc_id = title = court_name_v = court_pos = judge_name = all_sides = side_a = side_b = law_side_a = law_side_b = ""
    court_name_found = False
    court_types = ['שלום', 'מחוזי', 'עליון']

    # if(index > 0): break # break for testing
    for index, line in enumerate(text):
        __line = line.replace('\n', '')

        if('החלטה' in line):
            header = text[0:index+1]
            title = 'החלטה'
            break
        if('פסק דין' in line):
            header = text[0:index+1]
            title = 'פסק דין'
            break

        if('הצעה' in line):
            header = text[0:index+1]
            title = 'הצעה'
            break

    # find proc_id, court_name_v
    for index, item in enumerate(header[0:4]):
        item = item.strip('\u202c').strip('\u202b').strip('\u202a')

        # find the proc_id by extracting only the numbers part of it
        # if('תא' in item.replace('"', '') or 'תפ' in item.replace('"', '') or 'בל' in item.replace('"', '') or 'בעח' in item.replace('"', '') or 'דמ' in item.replace('"', '')):
        # if(False == proc_id):
        if(False == proc_id):
            proc_id_buffer = ''
            for char in item:
                if(char.isdigit() or '-' == char):
                    proc_id_buffer +=  char

            if(proc_id_buffer.__len__() > 4 and '-' in proc_id_buffer): # prediction that the proc_id should always have at least 4 digit including "-" char in it
                proc_id = proc_id_buffer

        # if not found, search on allias
        if('משפט' in item):
            court_pos = item.replace('בית המשפט', '').replace('בית משפט', '')

            for court in court_types:
                court_name = item.replace('בית המשפט', '').replace('בית משפט', '')
                if(court in court_name and False == court_name_found):
                    court_name_found = True
                    court_name_v = court
                court_pos = court_pos.replace('ה' + court, '').replace(court, '')
                if('ב' == court_pos[0]):
                    court_pos = court_pos[1]
        
        if('בית הדין האזורי לעבודה' in item or 'בית דין האזורי לעבודה' in item):
            court_name_v = 'בית הדין האזורי לעבודה'
            court_pos = item.replace('בית הדין האזורי לעבודה', '').replace('בית הדין האזורי לעבודה', '')

    # find judge_name
    for index, line in enumerate(header[0:10]):
        line = line.strip('\u202c').strip('\u202b').strip('\u202a')
        if('שופט' in line):
            judge_name = line

    
    # find all the people participating in the court hearing
    exclude_keywords = [
        'תובע',
        'תובעת',
        'תובעים',
        'תובעות',
        'נתבע',
        'נתבעת',
        'נתבעות',
        'נתבעים',
    ]
    all_sides = []
    for index, line in enumerate(header[0:30]):
        line = line.strip('\u202c').strip('\u202b').strip('\u202a')
        if(' ' not in line):
            matched = match_word_root(line)
            if(matched):
                side_type = line.replace(':', '')
                # print('matched at: .. searching within range: ' + str(line))
                # print('handler: ' + keys['handler'])
                # print('==========================')
                found = False

                # NOTE:: sometimes there can be multiple matches

                for x in range(3):
                    try:
                        if('' != header[index+x+1] and header[index+x+1] not in exclude_keywords):
                            if('.1' in str(header[index+x+1])):
                                # print('multi match detected, skipps..')
                                break
                            
                            
                            # if('3add251c7c010000090037f6a029e374.txt' == keys['handler']):
                            #     print('matched at: ' + str(index+x))
                            #     print(header[index+x+1])

                            found = True
                            all_sides.append({'type': side_type, 'matched': header[index+x+1]})
                            break
                    except: pass
                
                # if we didn't find in the upper range, search the lower range
                if(False == found):
                    for x in range(3):
                        try:
                            if('' != header[index-x-1] and header[index-x-1] not in exclude_keywords):
                                if('.1' in str(header[index-x-1])):
                                    # print('multi match detected, skipps..')
                                    break

                                found = True
                                all_sides.append({'type': side_type, 'matched': header[index-x-1]})
                                break
                        except: pass
                # print('==========================\r\n\r\n')

                
    return {
        'proc_id': proc_id.strip(),
        'court_pos': court_pos.strip(),
        'title': title.strip(),
        'court_name_v': court_name_v.strip(),
        'judge_name': judge_name.strip(),
        # 'side_a': all_sides
    }