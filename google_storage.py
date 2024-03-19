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


from google.api_core import exceptions
from google.api_core.retry import Retry
from google.cloud import storage


class GoogleStorage():        
    def __init__(self, bucket:str):
        self.bucket = bucket
        self.client = storage.Client()
        self._MY_RETRIABLE_TYPES = [
            exceptions.TooManyRequests,         # 429
            exceptions.InternalServerError,     # 500
            exceptions.BadGateway,              # 502
            exceptions.ServiceUnavailable,      # 503
        ]

    def __is_retryable(self, exc):
        return isinstance(exc, self._MY_RETRIABLE_TYPES)

    
    def upload(self, file, upload_to:str):
        """upload a file to google bucket storage

        Args:
            file (fileObject): the file object which supports read, write, etc
            upload_to (str): the destination on the bucket to write the file data to
        """
        
        my_retry_policy = Retry(predicate=self.__is_retryable)
        client = self.client.get_bucket(self.bucket, timeout=300, retry=my_retry_policy)
        blob = client.blob(upload_to)
        blob.upload_from_file(file, checksum='md5')