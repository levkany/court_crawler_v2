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


from typing import List
import re


def filter_str(string:str):
    return ''.join(c for c in string if c.isprintable())


def extract_court_name(lines:List[str]) -> str:
    """
    returns the first valid line since that 
    where the string we need located at
    """
    
    for line in lines:
        line = line.strip()
        if line:
            return filter_str(line)
    
    return ''


def extract_proc_id(lines:List[str]) -> str:
    """
    returns the id of the document if exists
    """
    
    pattern = r'(\d{4}|\d{5}|\d{6}|\d{7})-\d{2}-\d{2}'
    
    for line in lines:
        line = line.strip()
        if line:
            match = re.search(pattern, line)
            if match:
                return filter_str(match.group())
    
    return ''


def extract_judge(lines:List[str]) -> str:
    """
    returns the judge name if exists
    """
    
    for line in lines:
        line = filter_str(line.strip())
        if line:
            for word in line.split():
                if word == "כבוד" or word.startswith("כב'"):
                    return line
    
    return ''


def extract_type(lines:List[str]) -> str:
    """
    returns the type of the document
    """
    
    _types = ["החלטה", "פסק דין"]
    
    for line in lines:
        line = filter_str(line.strip())
        if line:
            if line in _types:
                return line
    
    return ''
