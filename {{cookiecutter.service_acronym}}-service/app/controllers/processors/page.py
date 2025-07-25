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
import json
from app.core import logger

from pdf2image import convert_from_path

from app.utils import constants as C
from app.utils import exceptions as E
from app.utils import utilities as U
from app.core.config import cfg
from app.controllers.AI import G_Model

_PAGE_FILTER = "Lab_Report"

def _format_class_response(class_response):
    """Format the classification response"""
    # [TODO] add rest of teh fields on change downstream
    if class_response["Classifier"]["Classifer_Status"] == "Success":
        return class_response["Classifier"]["Label"], 100, False, class_response["Model_Version"]
    else:
        return "Lab_Report", 0, True, class_response["Model_Version"]


def _format_page_class_response(
    _response,
    l1_label_details: dict = None,
    l2_label_details: dict = None,
    class_time=None,
    error_info=None,
):
    # Label - L1
    _L1_dict = {}
    if l1_label_details:
        _L1_dict["L1_Label"] = l1_label_details["page_label"]
        _L1_dict["L1_Label_Confidence"] = l1_label_details["conf_score"]
        _L1_dict["L1_Label_NHI"] = l1_label_details["class_NHI"]
    else:
        _L1_dict = None
    # LAbel - L2 => Not used as of now
    _L2_dict = {}
    if l2_label_details:
        _L2_dict["L2_Label"] = l2_label_details["page_label"]
        _L2_dict["L2_Label_Confidence"] = l2_label_details["conf_score"]
        _L2_dict["L2_Label_NHI"] = l2_label_details["class_NHI"]
    else:
        _L2_dict = None
    # Wrapper for L1 + L2 as Classification
    _class_dict = {}
    if _L1_dict or _L2_dict:
        status = "Success"
    else:
        status = "Error"
    _class_dict["Model_Version"] = _response["Model_Version"]
    _class_dict["Classification_Time"] = class_time
    _class_dict["Status"] = status
    _class_dict["Error_Info"] = error_info
    _class_dict["L1"] = _L1_dict
    _class_dict["L2"] = _L2_dict
    _response["Classification"] = _class_dict
    return _response


def process_page(pageid: str, info: dict, imagepath: str, process_info: dict, s3_path=None):
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
    _response = {
        "PageIDx": None,
        "Object_Store": None,
        "Page_Processing_Time": None,
        "Classification": {
            "Model_Version": None,
            "Classification_Time": None,
            "Status": None,
            "Error_Info": None,
            "L1": None,
            "L2": None,
        },
    }
    ocr_resp = None
    start_ts = time.time()
    info["PageIDx"] = pageid
    info["Pagename"] = imagepath.split("/")[-1]
    _log_prefix = U.set_log_prefix(**info)
    logger.info(f"{_log_prefix}- Begin processing page")
    image_s3_path = s3_path
    if not image_s3_path:
        # 0. Save image to S3
        image_s3_path = os.path.join(
            f"data/{info['Client_Name']}/{info['xxxTrxID']}/images",
            imagepath.split("/")[-1],
        )
        s3_save_start = time.time()
        logger.info(f"{_log_prefix}- Saving image to S3")
        # 0. Save to S3
        U.upload_file_to_s3(cfg=cfg, local_path=imagepath, s3_path=image_s3_path)
        s3_save_end = time.time()
        logger.info(f"{_log_prefix}- Image saved to S3 in {s3_save_end - s3_save_start} seconds")
    # --------------------------------------------------------------------------

    # format the Page info metadata
    _response["PageIDx"] = pageid + 1
    _response["Object_Store"] = U.build_store_path(cfg=cfg, postfix=image_s3_path)
    # --------------------------------------------------------------------------
    # 1. Determine Classification required
    ocrObj = None
    try:
        if process_info["Classifier"]:
            start_class = time.time()
            # 1. Perform OCR
            ocrObj = U.dertermine_ocr(cfg, "Classifier")
            ocr_resp = ocrObj.extract(info, imagepath)
            class_model = G_Model[cfg.models.Classifier.Model]
            class_response = class_model.Classify(image_path=imagepath, ocr_data=ocr_resp, info=info)
            # print("class_response:", class_response)
            page_label, conf_score, class_NHI, model_version = _format_class_response(class_response)
            end_class = time.time()
            logger.info(
                f"{_log_prefix}- Classification Response = {page_label}, {conf_score}, {class_NHI}, {model_version}"
            )
            logger.info(f"{_log_prefix}- Classification Time: {end_class - start_class}")
            # print("class_response:", class_response)
            resp_dict = {
                "page_label": page_label,
                "conf_score": conf_score,
                "class_NHI": class_NHI,
            }
            _response["Model_Version"] = model_version
            _response = _format_page_class_response(
                _response,
                l1_label_details=resp_dict,
                l2_label_details=None,
                class_time=(end_class - start_class),
                error_info=None,
            )
        else:
            # No classification required. Assumption non lab reports have been filterd out.
            logger.info(f"{_log_prefix}- Classification skipped")
            page_label = _PAGE_FILTER
            resp_dict = {
                "page_label": page_label,
                "conf_score": 100,
                "class_NHI": False,
                "model_version": "0.0.0",
            }
            _response = _format_page_class_response(
                _response,
                l1_label_details=resp_dict,
                l2_label_details=None,
                class_time=0,
                error_info=None,
            )
    except Exception as e:
        # We continue processing the page assuming the page is a Lab Report
        # The QC team or end client will ensure cleanup.
        logger.error(f"{_log_prefix}- Classification Error => {e}")
        page_label = _PAGE_FILTER
        _response = _format_page_class_response(
            _response,
            l1_label_details=None,
            l2_label_details=None,
            class_time=(time.time() - start_ts),
            error_info=f"Error-{e}",
        )
    # 0. Save classification ocr response to Object Store
    # ignore error -  non critical step
    try:
        if ocrObj:
            # .json
            json_filename = imagepath.replace(".jpg", ".json")
            print("json_filename:", json_filename)
            # save the ocr data to json
            with open(json_filename, "w") as f:
                json.dump(ocr_resp, f)
            # generate the S3 path
            class_ocr_save_start = time.time()
            ocr_filename = f"{cfg.models.Classifier.OCR}_class_" + imagepath.split("/")[-1].replace(".jpg", ".json")
            s3_path = os.path.join(f"data/{info['Client_Name']}/{info['xxxTrxID']}/ocr", ocr_filename)
            # Save to S3
            U.upload_file(cfg=cfg, local_path=json_filename, remote_path=s3_path)
            class_ocr_save_end = time.time()
            logger.info(
                f"{_log_prefix}- Classifier OCR saved to S3 in {class_ocr_save_end - class_ocr_save_start} seconds"
            )
    except Exception as e:
        # Ignore as non essential step
        logger.error(f"{_log_prefix}- Artifact Storage error - {e}")

    # --------------------------------------------------------------------------
    # 1. Check only for Lab_Reports
    if page_label != _PAGE_FILTER:
        _response["Extraction"] = None
        return _response

    # 2. Determine Extraction OCR
    ex_ocrObj = U.dertermine_ocr(cfg, "Digitizer")
    if ocrObj and cfg.models.Classifier.OCR != cfg.models.Digitizer.OCR:
        ocr_resp = ex_ocrObj.extract(info, imagepath)
    else:
        logger.info(f"{_log_prefix}- Once OCR")

    # 0. Saving OCR data to system
    try:
        if ex_ocrObj:
            json_filename = imagepath.replace(".jpg", ".json")
            print("json_filename:", json_filename)
            # save the ocr data to json
            with open(json_filename, "w") as f:
                json.dump(ocr_resp, f)

            extract_ocr_save_start = time.time()
            # generate the S3 path
            ocr_filename = f"{cfg.models.Digitizer.OCR}_extract_" + imagepath.split("/")[-1].replace(".jpg", ".json")

            s3_path = os.path.join(f"data/{info['Client_Name']}/{info['xxxTrxID']}/ocr", ocr_filename)
            # Save to S3
            U.upload_file(cfg=cfg, local_path=json_filename, remote_path=s3_path)
            extract_ocr_save_end = time.time()
            logger.info(
                f"{_log_prefix}- Digitizer OCR saved to S3 in {extract_ocr_save_end - extract_ocr_save_start} seconds"
            )
    except Exception as e:
        # ignore error -  non critical step
        logger.error(f"{_log_prefix}- Artifact Storage error - {e}")

    # 3. Perform Extraction
    # [TODO] May require change if version info is returned
    extract_start = time.time()
    extract_model = G_Model[cfg.models.Digitizer.Model]

    extract_response = extract_model.Digitize(image_path=imagepath, ocr_data=ocr_resp, info=info)
    extract_end = time.time()
    ex_model_version = extract_response["model_version"]
    # Format the response for extraction.
    _response["Page_Processing_Time"] = extract_end - start_ts
    # 4. Format reponse
    _extract_dict = {}
    _extract_dict["Model_Version"] = ex_model_version
    _extract_dict["Extraction_Time"] = extract_end - extract_start
    _extract_dict["Data"] = extract_response["response"]
    #
    _response["Extraction"] = _extract_dict
    logger.info(f"{_log_prefix}- Page Extraction Time : {extract_end - extract_start}")
    logger.info(f"{_log_prefix}- Page Processing Time : {extract_end - start_ts}")
    return _response
