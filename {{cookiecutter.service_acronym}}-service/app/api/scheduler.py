#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import os
import sys
import time
import json
from datetime import datetime
import tempfile

from fastapi import APIRouter, HTTPException, Response
from typing import Optional

from app.core import logger
from app.utils import utilities as U
from app.utils import constants as C
from app.utils import exceptions as E
from app.core.scheduler import Scheduler
from app.schema.schedule import CurrentScheduledJobsResponse
from app.controllers.jobs import importer
from app.controllers.jobs import exporter

router = APIRouter(prefix="/schedule")
# logger = logger.log_setup(cfg, "app")
# create a temporary directory for processing
temp_dirpath = tempfile.mkdtemp()


Scheduler.start()


@router.get("/list", response_model=CurrentScheduledJobsResponse)
async def Get_All_Schedules():
    """
    Will provide a list of currently Scheduled Tasks
    """
    try:
        schedules = []
        for job in Scheduler.get_jobs():
            schedules.append(
                {
                    "job_id": str(job.id),
                    "job_name": str(job.name),
                    "run_frequency": str(job.trigger),
                    "next_run": str(job.next_run_time),
                    "status": "Running" if str(job.next_run_time) != "None" else "Paused",
                }
            )
        return {"jobs": schedules}
    except Exception as e:
        logger.error(f"Error - {e}")
        return HTTPException(status_code=401, detail=f"Error - {e}")


@router.post("/importer/create")
async def Schedule_Importer_Job(
    import_id: str, queue_enum: Optional[str] = "default", seconds: int = 10, max_instances: int = 1
):
    """
    Add a New Job to a Schedule for a Importer
    """
    try:
        job = Scheduler.get_job(import_id)
        if job:
            return HTTPException(status_code=401, detail="Job Already Exists")

        name = datetime.now().strftime(r"%Y%m%d%H%M%S%f")
        job = Scheduler.add_job(
            importer.check_import_queue,
            trigger="interval",
            name=f"Importer-{name}",
            seconds=int(seconds),
            max_instances=max_instances,
            id=import_id,
            args=[queue_enum],
        )
        response = {
            "job_id": str(job.id),
            "job_name": str(job.name),
            "run_frequency": str(job.trigger),
            "next_run": str(job.next_run_time),
            "status": "Running",
        }
        logger.info(f"Importer Job Scheduled - {response}")
        return Response(
            content=json.dumps(
                response,
                indent=4,
                sort_keys=True,
                default=str,
            ),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error - {e}")
        return HTTPException(status_code=401, detail=f"Error - {e}")


@router.post("/importer/delete", response_model=CurrentScheduledJobsResponse)
async def Delete_Importer_Job(import_id: str):
    """
    Delete a Job for a Importer
    """
    try:
        job = Scheduler.get_job(import_id)
        job.remove()
        response = {
            "job_id": str(job.id),
            "job_name": str(job.name),
            "run_frequency": str(job.trigger),
            "next_run": str(job.next_run_time),
            "status": "Deleted",
        }
        logger.info(f"Importer Job Deleted - {response}")
        return Response(
            content=json.dumps(
                response,
                indent=4,
                sort_keys=True,
                default=str,
            ),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error - {e}")
        return HTTPException(status_code=401, detail=f"Error - {e}")


@router.post("/importer/job/pause", response_model=CurrentScheduledJobsResponse)
async def Pause_Importer_Job(import_id: str):
    """
    Pause a Job for a Importer
    """
    try:
        job = Scheduler.get_job(import_id)
        job.pause()
        response = {
            "job_id": str(job.id),
            "job_name": str(job.name),
            "run_frequency": str(job.trigger),
            "next_run": str(job.next_run_time),
            "status": "Paused",
        }
        logger.info(f"Importer Job Paused - {response}")
        return Response(
            content=json.dumps(
                response,
                indent=4,
                sort_keys=True,
                default=str,
            ),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error - {e}")
        return HTTPException(status_code=401, detail=f"Error - {e}")


@router.post("/importer/job/resume", response_model=CurrentScheduledJobsResponse)
async def Resume_Importer_Job(import_id: str):
    """
    Resume a Job for a Importer
    """
    try:
        job = Scheduler.get_job(import_id)
        job.resume()
        response = {
            "job_id": str(job.id),
            "job_name": str(job.name),
            "run_frequency": str(job.trigger),
            "next_run": str(job.next_run_time),
            "status": "Running",
        }
        logger.info(f"Importer Job Resumed - {response}")
        return Response(
            content=json.dumps(
                response,
                indent=4,
                sort_keys=True,
                default=str,
            ),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error - {e}")
        return HTTPException(status_code=401, detail=f"Error - {e}")


@router.get("/importer/list", response_model=CurrentScheduledJobsResponse)
async def Get_Importer_Jobs():
    """
    List all Jobs for importers
    """
    try:
        schedules = []
        for job in Scheduler.get_jobs():
            if "Importer-" in job.name:
                schedules.append(
                    {
                        "job_id": str(job.id),
                        "job_name": str(job.name),
                        "run_frequency": str(job.trigger),
                        "next_run": str(job.next_run_time),
                        "status": "Running" if str(job.next_run_time) != "None" else "Paused",
                    }
                )
        return {"jobs": schedules}
    except Exception as e:
        logger.error(f"Error - {e}")
        return HTTPException(status_code=401, detail=f"Error - {e}")


@router.post("/exporter/create")
async def Schedule_Exporter_Job(export_id: str, client_name: str = "xxx", seconds=10, max_instances=1):
    """
    Add a New Job to a Schedule for a exporter
    """
    try:
        name = client_name.upper().replace(" ", "_") + "-" + datetime.now().strftime(r"%Y%m%d%H%M%S%f")
        job = Scheduler.add_job(
            exporter.check_dispatch_queue,
            trigger="interval",
            name=f"Exporter-{name}",
            seconds=seconds,
            max_instances=max_instances,
            id=export_id,
            args=[client_name],
        )
        return Response(
            content=json.dumps(
                job,
                indent=4,
                sort_keys=True,
                default=str,
            ),
            media_type="application/json",
        )
    except Exception as e:
        return HTTPException(status_code=401, detail=f"Error - {e}")


@router.get("/exporter/list")
async def Get_Exporter_Jobs():
    """
    List all Jobs for exporters
    """
    try:
        schedules = []
        for job in Scheduler.get_jobs():
            if "Exporter-" in job.name:
                schedules.append(
                    {"job_id": str(job.id), "run_frequency": str(job.trigger), "next_run": str(job.next_run_time)}
                )
        return {"jobs": schedules}
    except Exception as e:
        return HTTPException(status_code=401, detail=f"Error - {e}")
