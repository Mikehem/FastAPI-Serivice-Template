#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import os
import json
import shutil
import time
from datetime import datetime
from typing import Union
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, Body, Header, Response

from app.core import logger
from pydantic import BaseModel
from app.utils import utilities as U
from app.utils import constants as C
from app.utils import exceptions as E
from app.core.config import cfg
from app.controllers.validators import document as V
from app.controllers.processors import document as PD
from app.controllers.processors import jwt_decode as JWT
from app.schema.request import Metadata, ProcessControl, User
from app.schema.response import DigitizerResponse
from app.controllers.dbo.mongo.client import MongoStore
from app.core.ltm import instrument, LTM
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

router = APIRouter(prefix="/document")
# create a temporary directory for processing
temp_dirpath = tempfile.mkdtemp()


# setup the default user
default_user = User(
    username="xxx",
    email="admin@xxx.in",
    default_centre_id="1",
    default_guest_id="1",
)

@instrument()
@router.post("/digitize")  # , response_model=DigitizerResponse)
async def Digitizer(
    document: UploadFile,
    info: Metadata = Body(...),
    process_info: ProcessControl = Body(
        None,
        examples=ProcessControl.model_config["json_schema_extra"]["examples"],
    ),
    access_token: Union[str, None] = Header(default=None),
):
    """API route to Digitizer Claims."""
    _response = {
        "Service": "{{cookiecutter.service_acronym}}",
        "Version": cfg.VERSION,
        "Transaction_Info": {"Transaction_ID": "1234", "Received_TS": "", "Status": "Open"},
        "Client_Info": None,
        "Request_Info": None,
        "Digitization": {},
        "QC": None,
        "Review": None,
    }
    # 1. Get the line items
    carrier = {}
    TraceContextTextMapPropagator().inject(carrier)
    OTEL_Trace_ID = carrier["traceparent"]
    start_time = time.time()
    start_dt = datetime.now()
    # Set Defaults
    info = info.dict()
    _response["Request_Info"] = info.copy()
    if "xxxTrxID" in info and info["xxxTrxID"]:
        trxId = info["xxxTrxID"]
    else:
        trxId = OTEL_Trace_ID
        info["xxxTrxID"] = trxId

    _response["Transaction_Info"]["Transaction_ID"] = trxId

    # [Done] - use header client info to fill data
    client_info_dict = JWT.get_client(access_token)
    if client_info_dict:
        _response["Client_Info"] = client_info_dict.dict()
    else:
        _response["Client_Info"] = default_user.dict()
        client_info_dict = default_user

    info["Client_Name"] = client_info_dict.username

    if process_info is None:
        process_info = {}
        process_info["Classification"] = True
        process_info["Pages"] = [-1]
        process_info["QC"] = cfg.processing.QC.default
    else:
        process_info = process_info.dict()
    #
    _log_prefix = U.set_log_prefix(**info)
    logger.info(f"{_log_prefix}-{C.HEADER_10} Received Request {C.HEADER_10}")
    # 2. Validate the File
    try:
        # intial validation
        V.validate_filetype(trxId, document)
        # read the uploaded file
        file_data = await document.read()
        # write the file to temperory directory for processing
        upload_dir = os.path.join(temp_dirpath, trxId)
        os.makedirs(upload_dir, exist_ok=True)
        upload_filepath = os.path.join(upload_dir, document.filename)  # f'./uploads/{txn_id}_{file.filename}'
        info["Filename"] = document.filename
        with open(upload_filepath, "wb") as upload_file:
            upload_file.write(file_data)
    except E.InvalidFileType as e:
        logger.error(f"-{_log_prefix}-{e}", exc_info=True)
        raise HTTPException(status_code=411, detail=f"Error - {e}.")
    except Exception as e:
        logger.error(f"-{_log_prefix}-{e}", exc_info=True)
        raise HTTPException(status_code=411, detail=f"Error - Please Try again.")

    try:
        # Begin process
        logger.info(f"{_log_prefix}-Begin Processing Request")
        # 1. Start processing the document
        results = PD.process_document(
            info=info, fileId="1", filetype=document.content_type, filepath=[upload_filepath], process_info=process_info
        )
        # 2. Start Processing the response
        # 3. Persist the data
        end_time = time.time()
        logger.info(f"{_log_prefix}-Time Taken : {end_time - start_time}")
        end_dt = datetime.now()
        _response["Transaction_Info"]["Received_TS"] = start_dt
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
        _response["Transaction_Info"]["Status"] = "Error"
        _response["Transaction_Info"]["Error"] = str(e)
        dbo = MongoStore(db=cfg.store.mongodb.db, collection=cfg.store.mongodb.collection.report)
        saved_doc = dbo.InsertDocument(lab_doc=_response)
        raise HTTPException(status_code=418, detail=f"There's an error uploading file. Please try again!!!")

    logger.debug(f"{_log_prefix}- Response Request => {_response}")
    # Cleanup the system
    shutil.rmtree(os.path.join(temp_dirpath, trxId))

    return Response(
        content=json.dumps(json.loads(saved_doc), indent=4, sort_keys=True, default=str),
        media_type="application/json",
    )
