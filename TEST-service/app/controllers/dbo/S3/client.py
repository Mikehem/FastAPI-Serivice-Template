#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import uuid
import json
from bson import json_util
from datetime import datetime, timezone

from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from fastapi import FastAPI, Body, HTTPException, status

import boto3

from app.utils import exception as E 
from app.core.config import cfg

class S3Store():
    def __init__(self):
        self.session = boto3.Session(
        aws_access_key_id = cfg.store.S3.Object_Store.id,
        aws_secret_access_key =  cfg.store.S3.Object_Store.key)
        self.s3 = self.session.client('s3')
        self.bucket = self.s3.Bucket(cfg.store.S3.Object_Store.bucketName)
    
    def get_object(self):
        pass
    
    def put_object(self, file_path:str, s3_path:str):
        self.s3.upload_file(file_path, 
                            cfg.store.S3.Object_Store.bucketName,
                            s3_path)
        return True