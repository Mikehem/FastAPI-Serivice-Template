#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
from urllib.parse import quote_plus
from pymongo import MongoClient

from app.core.config import cfg


# APScheduler Related Libraries
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.job import Job

password = quote_plus(cfg.store.mongodb.password)
url = f"{cfg.store.mongodb.url_prefix}{cfg.store.mongodb.username}:{password}@{cfg.store.mongodb.server}{cfg.store.mongodb.url_postfix}"
client = MongoClient(url, connect=False)

jobstores = {
    "default": MongoDBJobStore(
        database=cfg.store.mongodb.db, collection=cfg.store.mongodb.collection.schedule, client=client
    )
}

Scheduler = BackgroundScheduler(jobstores=jobstores)
