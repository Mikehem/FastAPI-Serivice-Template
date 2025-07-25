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
from urllib.parse import quote_plus

from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from fastapi import FastAPI, Body, HTTPException, status

import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from app.utils import exceptions as E
from app.core.config import cfg


class MongoStore:
    def __init__(self, db: str, collection: str):
        """Initialize the Mongo Client."""
        password = quote_plus(cfg.store.mongodb.password)
        url = f"{cfg.store.mongodb.url_prefix}{cfg.store.mongodb.username}:{password}@{cfg.store.mongodb.server}{cfg.store.mongodb.url_postfix}"
        self.client = MongoClient(url, connect=False)
        self.db = self.client[db]
        self.collection = self.db[collection]

    def GetDocuments(self):
        pass

    def GetDocument(self, oid: str):
        """Get the document by id."""
        try:
            doc = self.collection.find_one({"_id": oid})
            return json.dumps(doc, default=json_util.default, indent=4)
        except Exception as e:
            raise E.DBJobError(message=f"Error getting document from DB - {e}")

    def InsertDocument(self, lab_doc: dict):
        """Insert the extracted document to database."""
        try:
            new_doc = self.collection.insert_one(lab_doc)
            created_doc = self.collection.find_one({"_id": new_doc.inserted_id})
            return json.dumps(created_doc, default=json_util.default, indent=4)
        except DuplicateKeyError as e:
            raise E.DBJobError(message=f"Duplication Error for document - {e}")
        except Exception as e:
            raise E.DBJobError(message=f"Error saving to document to DB - {e}")

    def UpdateDocument(self):
        pass
