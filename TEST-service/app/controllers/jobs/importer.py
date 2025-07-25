#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import json
import time
import os

import tempfile
import shutil
from datetime import datetime

from joblib import Parallel, delayed
from typing import Union
from pydantic import BaseModel

# from PyPDF2 import PdfMerger
from PIL import Image

from app.core import logger
from app.core.config import cfg
from app.utils import utilities as U
from app.utils import constants as C
from app.utils import exceptions as E
from app.controllers.processors import document as PD
from app.controllers.processors import page as PP
from app.controllers.dbo.mongo.client import MongoStore
from app.schema.request import Metadata, ProcessControl, User, _File

from xxxai.datastore.AWS.SQS.sqs_client import SQS_Client
from xxxai.datastore.AWS.S3.dao import DAO

temp_dirpath = tempfile.mkdtemp()

_RESPONSE = {
    "Transaction_Info": {"Transaction_ID": "1234", "Received_TS": "", "Status": "Open"},
    "Client_Info": None,
    "Request_Info": None,
    "Digitization": {},
    "QC": None,
    "Review": None,
}


def _filter_pages(s3_paths: list, process_info: dict):
    """Check if pages need to be filtered for classification."""
    lab_page_list = []
    if not process_info["Classifier"] and process_info["Pages"][0] != -1:
        lab_page_list = []
        for i, page in enumerate(s3_paths):
            if i + 1 in process_info["Pages"]:
                lab_page_list.append(page)

    return lab_page_list


def _process_pages():
    pass


default_user = User(
    username="xxx",
    email="admin@xxx.in",
    center_id="1",
    guest_id="1",
)


def check_import_queue(queue_cfg: str = "default"):
    """Processes SQS messages"""
    _response = _RESPONSE.copy()
    info = {}
    if queue_cfg not in cfg.store.SQS[queue_cfg].keys():
        queue_cfg = "default"
    queue = cfg.store.SQS[queue_cfg].Queue
    region = cfg.store.SQS[queue_cfg].Region
    access_key = cfg.store.SQS[queue_cfg].Access_Key
    secret_key = cfg.store.SQS[queue_cfg].Secret_Key
    # Initialise the SQS  client and read message
    sqs_client = SQS_Client(region, queue, access_key, secret_key)
    sqs_message = sqs_client.receive_and_delete_message()
    # Process the message if received
    if sqs_message != None and sqs_message != "Failed":
        logger.info(f"{C.HEADER_10} Received SQS Message {C.HEADER_10}")
        logger.info(f"{C.HEADER_10} {sqs_message} {C.HEADER_10}")
        # Get all the data elements
        file_paths = json.loads(sqs_message["Messages"][0]["Body"])["S3_Path"]
        request_info = json.loads(sqs_message["Messages"][0]["Body"])["Request_Info"]
        request_info = Metadata(**request_info)
        # 1 Validate Requestm Info
        if not isinstance(request_info, Metadata):
            logger.error(f"{C.HEADER_10} Invalid Request Info {C.HEADER_10}")
            raise E.InvalidRequestInfo(request_info)
        info = request_info.dict().copy()

        process_info = json.loads(sqs_message["Messages"][0]["Body"])["Process_Info"]
        process_info = ProcessControl(**process_info)
        # 2. Validate the Process Info
        # 2.1 Check if the process info is valid of type ProcessControl
        if not isinstance(process_info, ProcessControl):
            logger.error(f"{_log_prefix}-{C.HEADER_10} Invalid Process Info {C.HEADER_10}")
            raise E.InvalidProcessInfo(process_info)

        client_info = json.loads(sqs_message["Messages"][0]["Body"])["Client_Info"]
        client_info = User(**client_info)
        # 3. Validate the Client Info
        # 3.1 Check if the client info is valid of type User
        if not isinstance(client_info, User):
            logger.error(f"{_log_prefix}-{C.HEADER_10} Invalid Client Info {C.HEADER_10}")
            raise E.InvalidClientInfo(client_info)

        _response["Request_Info"] = request_info.dict()

        if process_info is None:
            process_info = {}
            process_info["Classification"] = True
            process_info["Pages"] = [-1]
            process_info["QC"] = cfg.processing.QC.default
        else:
            process_info = process_info.dict()

        if client_info is None:
            client_info = default_user.dict()
        else:
            client_info = client_info.dict()

        _response["Client_Info"] = client_info
        info["Client_Name"] = client_info["username"]

        start_time = time.time()
        start_dt = datetime.now()
        if "xxxTrxID" in info and info["xxxTrxID"]:
            trxId = info["xxxTrxID"]
        else:
            trxId = start_dt.strftime(r"%Y%m%d%H%M%S%f")
            info["xxxTrxID"] = trxId

        _response["Transaction_Info"]["Transaction_ID"] = trxId

        _log_prefix = U.set_log_prefix(**info)
        logger.info(f"{_log_prefix}-{C.HEADER_10} Received Request {C.HEADER_10}")

        if len(file_paths) > 1:
            file_types = [U.get_file_type(file_path) for file_path in file_paths]
            if len(set(file_types)) > 1:
                logger.error(f"{_log_prefix}-{C.HEADER_10} Multiple File Types {C.HEADER_10}")
                raise E.MultipleTypesFound(trxId, file_types)
            if file_types.count(".pdf") > 1:
                logger.error(f"{_log_prefix}-{C.HEADER_10} Multiple PDF Files {C.HEADER_10}")
                raise E.MultiplePDFFiles(trxId, file_types)

        #   3.2 Validate non standard file types
        # for file in file_paths:
        #     file_name = U.get_file_name(file)
        #     name, status = U.check_standard_file_type(file_name)
        #     if not status:
        #         logger.error(f"{_log_prefix}-{C.HEADER_10} Invalid File Type {C.HEADER_10}")
        #         raise E.InvalidFileType(trxId, name)

        upload_filepath = []
        file_path_list = []

        for i, s3_url in enumerate(file_paths):
            start_time = time.time()
            start_dt = datetime.now()
            s3_bucket = U.get_bucket_name(s3_url)
            s3_file_path = U.get_file_path(s3_url)
            content_type = U.get_file_content_type(s3_file_path)
            file_name = U.get_file_name(s3_file_path)
            s3_client = DAO(s3_bucket, cfg.store.Object_Store.S3.Access_Key, cfg.store.Object_Store.S3.Secret_Key)
            s3_file_data = s3_client.get_file_from_s3_byte(s3_file_path)
            file_obj = _File(filename=file_name, file_data=s3_file_data, content_type=content_type)

            # 4.0 Save files to local -> Temp folder
            upload_dir = os.path.join(temp_dirpath, trxId)
            os.makedirs(upload_dir, exist_ok=True)
            upload_filepath = os.path.join(upload_dir, file_obj.filename)
            info["Filename"] = file_obj.filename
            with open(upload_filepath, "wb") as upload_file:
                upload_file.write(file_obj.file_data)
            file_path_list.append(upload_filepath)

        # if len(file_path_list) > 1:
        #     # 4.1 Merge the files
        #     file_obj = _File(filename=f"{trxId}.pdf", file_data=None, content_type="application/pdf")
        #     upload_filepath = os.path.join(upload_dir, file_obj.filename)
        #     info["Filename"] = f"{trxId}.pdf"
        #     images = [Image.open(x) for x in file_path_list]
        #     images[0].save(upload_filepath, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
        try:
            # Begin process
            logger.info(f"{_log_prefix}-Begin Processing Request")
            # 1. Start processing the document
            results = PD.process_document(
                info=info,
                fileId="1",
                filetype=file_obj.content_type,
                filepath=file_path_list,
                process_info=process_info,
                call_type_internal=True,
                s3_paths=file_paths,
            )
            # 2. Start Processing the response
            # 3. Persist the data
            end_time = time.time()
            logger.info(f"{_log_prefix}-Time Taken : {end_time - start_time}")
            end_dt = datetime.now()
            _response["Transaction_Info"]["Received_TS"] = start_dt

            if "Request_TS" in info.keys() and info["Request_TS"]:
                _response["Transaction_Info"]["Request_TS"] = info["Request_TS"]
            else:
                _response["Transaction_Info"]["Request_TS"] = start_dt
            # set QC Status based on process_info
            if "QC" in process_info.keys() and process_info["QC"]:
                _response["Transaction_Info"]["Status"] = "QC_Pending"
                _response["Transaction_Info"]["QC_Required"] = True
            else:
                _response["Transaction_Info"]["Status"] = "QC_Ignored"
                _response["Transaction_Info"]["QC_Required"] = False

            # Add Priority
            if "Priority" in process_info.keys() and process_info["Priority"]:
                _response["Transaction_Info"]["Priority"] = process_info["Priority"]
            else:
                _response["Transaction_Info"]["Priority"] = "Normal"
            if "Data_Path" in info.keys() and info["Data_Path"]:
                _response["Transaction_Info"]["Data_Path"] = info["Data_Path"]
            else:
                _response["Transaction_Info"]["Data_Path"] = results["Object_Store"]

            # Save Digitization Info
            _response["Digitization"] = {"Digitization_Time": "", "Files": []}
            _response["Digitization"]["Digitization_Time"] = end_time - start_time
            _response["Digitization"]["Files"].append(results)
            # Save to Database
            dbo = MongoStore(db=cfg.store.mongodb.db, collection=cfg.store.mongodb.collection.report)
            saved_doc = dbo.InsertDocument(lab_doc=_response)
            logger.debug(f"{_log_prefix}- Saved to database => {saved_doc}")
        except Exception as e:
            logger.error(f"{_log_prefix}- {e}", exc_info=True)
            logger.debug(f"{_log_prefix}- Response Request => {_response}")
            # Save to Database
            _response["Transaction_Info"]["Status"] = "Error"
            _response["Transaction_Info"]["Error"] = str(e)

            dbo = MongoStore(db=cfg.store.mongodb.db, collection=cfg.store.mongodb.collection.report)
            saved_doc = dbo.InsertDocument(lab_doc=_response)
        # Cleanup the system
        shutil.rmtree(os.path.join(temp_dirpath, trxId))
    # 4.1 If pdf -> process file else
    # 4.2 If images -> format {"fileidx": "1", "image_paths": image_paths}
    # -----------------------------------------------
    # 5. Filter images as per Process Flow
    # 5. image list -> process page [wrapper] => copy from process_document
    # 5. Format response
    # 6. Save to Db
