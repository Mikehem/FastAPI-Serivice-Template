#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
from enum import Enum
from pydantic import BaseModel
from typing import Optional

from app.schema.transaction import TransactionInfo

class ResponseInfo(BaseModel):
    Transaction_Info: TransactionInfo
    
class Process_Control(BaseModel):
    Classifier: bool
    
class DigitizerResponse(BaseModel):
    Classifier: bool
