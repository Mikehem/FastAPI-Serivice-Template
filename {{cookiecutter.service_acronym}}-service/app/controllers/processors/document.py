#####################################################################
# Copyright(C), {{cookiecutter.devleopment_year}} xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
"""File Controller specific methods.

This provides a suite of methods to control the flow of logic
for files received for processing.

  Typical usage example:
  
  result = file._specif_Function(parameters)
"""
import os
import time
from datetime import datetime
from app.core import logger
from typing import List
from joblib import Parallel, delayed, parallel_backend

from pdf2image import convert_from_path

from app.utils import constants as C
from app.utils import exceptions as E
from app.utils import utilities as U
from app.core import cfg
from app.controllers.processors import page as PP


def process_file(info: dict, filepath: str, filetype: str):
    if filetype == C.MIME_PDF:
        # PUT TNX ID in PROD
        file_dir = os.path.dirname(os.path.realpath(filepath))
        image_folder = os.path.join(file_dir, "images")  # f'./pdf_to_image/{txn_id}/'
        os.makedirs(image_folder, exist_ok=True)
        print(image_folder)
        image_paths = convert_from_path(
            pdf_path=filepath,
            size=2400,
            output_folder=image_folder,
            output_file="p",  # prefix
            thread_count=8,
            fmt="jpeg",
            paths_only=True,
        )
    elif filetype == C.MIME_IMAGE:
        image_paths = [filepath]
    else:
        raise E.InvalidFileType(info["xxxTrxID"], info["FileIDx"], filepath.strip("/")[-1])
    return {"fileidx": info["FileIDx"], "image_paths": image_paths}


def process_document(
    info: dict,
    fileId: str,
    filetype: str,
    filepath: list,
    process_info: dict,
    call_type_internal: bool = False,
    s3_paths: list = None,
):
    """Process each file provided during request.

    Process each file for page extractions.

    Args
    ----
        trxId: The request transaction ID. Used for logging purpose.
        lines: List of bill particular lines

    Returns
    -------
        The classes for each line.
        example:

    Raises
    ------

    """
    _response = {"Files": []}
    info["FileIDx"] = fileId
    _log_prefix = U.set_log_prefix(**info)
    s3_path = None
    pages = None
    if not call_type_internal:
        s3_path = os.path.join(f"data/{info['Client_Name']}/{info['xxxTrxID']}", filepath[0].split("/")[-1])
        # 0. Save to S3
        U.upload_file(cfg=cfg, local_path=filepath[0], remote_path=s3_path)
        # 1. Process the file to get pages
        pages = process_file(info=info, filepath=filepath[0], filetype=filetype)
        # ---------------------------------------------------------------------
    else:
        s3_path = "/".join(s3_paths[0].split("/")[0:-1])
        if filetype == C.MIME_PDF:
            pages = process_file(info=info, filepath=filepath[0], filetype=filetype)
            s3_path = s3_path
            s3_paths = None
        else:
            pages = {"fileidx": info["FileIDx"], "image_paths": filepath}
        # ---------------------------------------------------------------------

    total_pages = len(pages["image_paths"])
    logger.info(f"{_log_prefix}- Total Pages : {len(pages['image_paths'])}")
    if len(pages["image_paths"]) < 1:
        raise E.ProcessingError(
            message="Page Extraction error from document.", value={"Extracted Pages": len(pages["image_paths"])}
        )
    # 2. Determine pages to process
    if not process_info["Classifier"] and process_info["Pages"][0] != -1:
        lab_page_list = []
        for i, page in enumerate(pages["image_paths"]):
            if i + 1 in process_info["Pages"]:
                lab_page_list.append(page)
        pages["image_paths"] = lab_page_list

    # Raise error - most probably the incorrect pages were provided by user
    if len(pages["image_paths"]) < 1:
        raise E.ProcessingError(
            message="Page Extraction error- Please check page index provided in process flow.",
            value={"Process.Pages": process_info["Pages"]},
        )
    # 3. Multiprocess each page item
    n_jobs = cfg.processing.Parallelization.Job_count
    backend = cfg.processing.Parallelization.backend
    logger.info(f"{_log_prefix}- Joblib parameters : {n_jobs}, {backend}")
    print("Joblib parameters [n_jobs, backend]:", n_jobs, backend)
    start_pages_proc = time.time()
    results = Parallel(n_jobs=n_jobs, backend=backend)(
        delayed(PP.process_page)(i, info, filepath, process_info, s3_paths[i] if s3_paths else None)
        for i, filepath in enumerate(pages["image_paths"])
    )
    # Format the response
    end_pages_proc = time.time()
    logger.info(f"{_log_prefix}- Document Processing Time : {end_pages_proc - start_pages_proc}")
    _results = {}
    _results["FileIDx"] = "1"
    _results["Filename"] = info["Filename"]
    _results["Total_Pages"] = total_pages
    _results["Total_Processed_Pages"] = len(pages["image_paths"])
    _results["Object_Store"] = U.build_store_path(cfg=cfg, postfix=s3_path)
    _results["Processed_TS"] = datetime.now()
    _results["File_Processing_Time"] = end_pages_proc - start_pages_proc
    _results["Pages"] = results
    return _results
