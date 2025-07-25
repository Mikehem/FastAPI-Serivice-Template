#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
from fastapi import APIRouter

_VERSION = "1.0.0"
router = APIRouter(prefix="/admin")

@router.get("/healthz")
async def healthz():
    return {"Status": "OK"}

@router.get("/version")
async def version():
    return {"Version": _VERSION}

@router.get("/info")
async def info():
    return {"Version": _VERSION}

# add checks for downstream APIs in microservice