
#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
# DATABASE CLASS
import pymongo
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.uri_parser import parse_uri
from urllib.parse import quote_plus
from app.core.config import cfg

class MongoStore:
    """
    | This can be used to connect to a mongodb instance,
    insert documents into collection, retrieve documents through query
    """

    def __init__(self):
        dbstore = cfg.store.mongodb
        self.uri = dbstore.MongoClient
        conn = pymongo.MongoClient(self.uri)
        db = conn[dbstore.db]
        self.collection = db[dbstore.collection.standardisation]

    # Add document to the collection
    def insert_one_rec(self, obj):
        x = self.collection.insert_one(obj)
        return x.inserted_id

    def find_one_and_update(self, query, obj):
        return self.collection.find_one_and_update(query, {'$set': obj},return_document=ReturnDocument.AFTER,
                                                upsert=True)

    def insert_or_update(self, obj):
        try:
            x = self.collection.insert_one(obj)
            return x.inserted_id
        except DuplicateKeyError as e:
            query = obj["_id"]
        return self.collection.find_one_and_update(query, {'$set': obj},return_document=ReturnDocument.AFTER)

    # Get all the documents in the collection
    def get_all_records(self) -> list:
        return list(self.collection.find())

    # Search for the document using query
    def search_rec(self, query:str) -> list:
        mydoc = self.collection.find(query, {"map":1,"_id":0})
        return list(mydoc)
