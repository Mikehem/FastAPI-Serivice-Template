#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
from pydantic import BaseModel, Field
from typing import List


class CurrentScheduledJob(BaseModel):
    job_id: str = Field(title="The Job ID in APScheduler", description="The Job ID in APScheduler")
    job_name: str = Field(title="The Job Name in APScheduler", description="The Job Name in APScheduler")
    run_frequency: str = Field(title="The Job Interval in APScheduler", description="The Job Interval in APScheduler")
    next_run: str = Field(title="Next Scheduled Run for the Job", description="Next Scheduled Run for the Job")
    status: str = Field(title="The Status of the Job", description="The Status of the Job")

    model_config = {
        "schema_extra": {
            "example": {
                "job_id": "001",
                "job_name": "20221110221209397",
                "run_frequency": "interval[0:05:00]",
                "next_run": "2020-11-10 22:12:09.397935+10:00",
                "status": "running",
            }
        }
    }


class CurrentScheduledJobsResponse(BaseModel):
    jobs: List[CurrentScheduledJob]


class JobCreateDeleteResponse(BaseModel):
    scheduled: bool = Field(
        title="Whether the job was scheduled or not", description="Whether the job was scheduler or not"
    )
    job_id: str = Field(title="The Job ID in APScheduler", description="The Job ID in APScheduler")

    model_config = {"schema_extra": {"example": {"scheduled": True, "job_id": "www.xxx.in"}}}
