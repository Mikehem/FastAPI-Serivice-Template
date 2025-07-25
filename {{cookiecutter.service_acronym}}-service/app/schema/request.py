#####################################################################
# Copyright(C), {{cookiecutter.devleopment_year}} xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import json
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Union
from enum import Enum
from datetime import datetime


class _Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class _File(BaseModel):
    filename: str
    content_type: str
    file_data: bytes = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    center_id: Union[str, None] = None
    guest_id: Union[str, None] = None


class Metadata(BaseModel):
    ClientTrxID: str
    Request_TS: Optional[str] = Field(default=datetime.now().strftime(r"%Y%m%d%H%M%S%f"), title="Request Time Stamp")
    Data_Path: Optional[str] = Field(default=None, title="Data Path")
    Client_Name: Optional[str] = Field(default=None, title="Client Name", max_length=30)
    GuestID: Optional[str] = Field(default=None, title="some description..", max_length=30)
    CenterID: Optional[str] = Field(default=None, title="Some Description.", max_length=30)
    xxxTrxID: Optional[str] = Field(default=None, title="Internal xxx Transaction ID. ignore for direct calls.", max_length=30)

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {"example": {"ClientTrxID": "1234"}},
    }


class ProcessControl(BaseModel):
    Classifier: bool
    Pages: Optional[List[int]] = [-1]
    QC: bool = True
    Mail_List: Optional[List[str]] = None
    Priority: _Priority = "LOW"

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "A standard process control flow.",
                    "description": "A **standard** process control with classification followed by Digitization.",
                    "value": {"Classifier": True, "Pages": None, "QC": True, "Mail_List": None},
                },
                {
                    "summary": "No Classification.",
                    "description": "**No** Classification required all pages are Lab Reports.",
                    "value": {"Classifier": False, "Pages": [-1], "QC": False, "Mail_List": None},
                },
                {
                    "summary": "Process Specific Pages.",
                    "description": "**No** Classification required specific pages digitization.",
                    "value": {"Classifier": False, "Pages": [1], "QC": True, "Mail_List": None},
                },
            ]
        }
    }


class ImporterQueueEnum(str, Enum):
    SQS = "SQS"


class ImporterSQSQueueInfo(BaseModel):
    Queue: ImporterQueueEnum = "SQS"
    Region: str
    Access_Key: str
    Secret_Key: str

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "Queue": "SQS",
                "Region": "",
                "Access_Key": "",
                "Secret_Key": "",
            }
        },
    }
