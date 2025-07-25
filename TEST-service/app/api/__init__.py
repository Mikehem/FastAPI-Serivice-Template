#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
from fastapi import APIRouter

from app.api import admin
from app.api import digitization
# from app.api import scheduler

api_router = APIRouter()

api_router.include_router(admin.router, tags=["Administration"])
# api_router.include_router(scheduler.router, tags=["Scheduler"])
api_router.include_router(digitization.router, tags=["Digitization"])