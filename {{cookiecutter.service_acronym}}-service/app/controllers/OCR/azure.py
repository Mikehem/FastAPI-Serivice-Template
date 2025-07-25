#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
"""Local Pytesseract Implementation of the abastract class - AbstractOCRExtractor.

This class implements the pytesseract OCR, through a python API call.

  Typical usage example:
  
  ocrObj = pyTesseractOCR(cfg:OmeagaConf)
"""

import json
import os
import re
import ast
import numpy as np
import time

import requests
from requests import get, post

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient

from app.core import logger
from app.utils import exceptions as E
from app.utils import utilities as U 
from app.utils import constants as C
from app.core.config import cfg
from app.controllers.OCR.abstract_ocr import AbstractOCRExtractor

# Local Constants
_SUCCESS = "succeeded"
_FAILED = "failed"

class AzureLayoutOCR(AbstractOCRExtractor):
    def __init__(self):
        """Initialises the class."""
        self.Name = "Azure Layout OCR"
        self.client = None
        self.form_path = None
        self.text = None
        self._config()

    def _config(self) -> None:
        self.endpoint = cfg.models.OCR.Azure_Layout.endpoint
        self.apim_key = cfg.models.OCR.Azure_Layout.Key

        # Form recognizer client is the SDK of azure layout
        self.headers = {
            # Request headers
            "Content-Type": C.MIME_IMAGE,
            "Ocp-Apim-Subscription-Key": self.apim_key,
        }
    
    def _submitJob(self, info, image_bytes) -> str:
        """Submits a job for action to Azure."""
        try:
            resp = requests.post(url=self.endpoint, data=image_bytes, headers=self.headers)
            # Response 202
            # Request is queued successfully.
            if resp.status_code != 202:
                raise E.AzureJobSubmissionFailure(info["xxxTrxID"], info["FileIDx"], info["PageIDx"], resp.json())
            # Succesful job submitted
            job_url = resp.headers["operation-location"]
        except Exception as e:
            raise E.AzureJobSubmissionFailure(info["xxxTrxID"], info["FileIDx"], info["PageIDx"], e)
        return job_url

    def _checkJobStatus(self, info, job_url):
        """Gets the job response from azure."""
        try:
            resp = requests.get(url=job_url, headers={"Ocp-Apim-Subscription-Key": self.apim_key})
            resp_json = resp.json()
            if resp.status_code != 200:
                raise E.AzureJobFailure(info["xxxTrxID"], info["FileIDx"], info["PageIDx"], resp_json)
            status = resp_json["status"]
            if status == _SUCCESS:
                return resp_json
            if status == _FAILED:
                raise E.AzureJobFailure(info["xxxTrxID"], info["FileIDx"], info["PageIDx"], resp_json)
            return None
        except Exception as e:
            # msg = "GET analyze results failed with Error : "+e
            raise E.AzureJobFailure(info["xxxTrxID"], info["FileIDx"], info["PageIDx"], e)


    def extract(
        self,
        info:dict,
        image_path: str
    ):
        """Main function call to perform OCR.

        This function call is used to call the OCR functionality.

        Args
        ----
            info: The request details. Used for logging purpose.
            images_folder: Full path to the images folder to perform OCR.
            postprocess: Boolean value to run postprocess. Default False.
            outfilepath: Full path in case the OCR output needs to be saved.

        Returns
        -------
            The JSON response for the OCR API call.

        Raises
        ------
            AzureJobFailure: In case the OCR job failed.
            AzureJobSubmissionFailure: In case  the job could not be submitted.

        """
        # Check if Dev Saver is on
        _log_prefix = U.set_log_prefix(**info)
        logger.info(f"{_log_prefix}- Begin OCR page")
        ocr_filename = None
        try:
            if cfg.models.OCR.Dev_Saver:
                # Search for filename in data folder if found return else follow through
                filename = info["Filename"]
                filename = filename.replace("."+filename.split(".")[-1], "")
                pagename = info['Pagename'].replace(".jpg","")
                ocr_filename = f"{filename}_{pagename}.json"
                data = None
                if os.path.isfile(os.path.join("data/ocr", ocr_filename)):
                    with open(os.path.join("data/ocr", ocr_filename), "r") as f:
                        data = json.loads(f.read())
                if data:
                    logger.info(f"{_log_prefix}- Return Local OCR page")
                    return data
        except Exception as e:
            logger.warn(f"{_log_prefix}- Local document extraction failed - {e}")
        # Local Extraction not possible or present call API
        logger.info(f"{_log_prefix}- Return new OCR page")
        try:
            image_bytes = bytearray(U.read_image_bin(image_path))
            # Send the request job
            job_url = self._submitJob(info, image_bytes)
            # get the response polling for predetermined time
            job_checks = 0
            response = None
            while job_checks < cfg.models.OCR.Azure_Layout.pole_tries and response is None:
                response = self._checkJobStatus(info, job_url)
                time.sleep(cfg.models.OCR.Azure_Layout.pole_wait_secs)
                job_checks += 1
            try:    
                if response and cfg.models.OCR.Dev_Saver:
                    os.makedirs("data/ocr", exist_ok=True)
                    logger.info(f"{_log_prefix}- Save Local OCR page - {ocr_filename}")
                    with open(os.path.join("data/ocr", ocr_filename), 'w') as f:
                        json.dump(response, f)
            except Exception as e:
                logger.warn(f"{_log_prefix}- Local document saving failed - {e}")
            return response
        except Exception as e:
            raise E.OCRError(info["xxxTrxID"], info["FileIDx"], info["PageIDx"])


    def postprocess(self, info, extract_response) -> str:
        """Extracts all text portion from OCR data.

        The post processing specific logic extracts all the text and returns it
        as a string tot he calling program.

        Args
        ----
            extract_response: The JSON Response from the OCR API call.

        Returns
        -------
            DataFrame: Azure detected tables as pandas dataframe.

        Raises
        ------
            None

        """
        # 1. Get the content for all pages within the document.
        #   - code is written for multiple pages to be generic but in the cbd flow
        #     only one page is sent at a time.
        info["OCR"] = self.Name
        _log_prefix = U.set_log_prefix(**info)
        start_preproc = time.time()
        logger.info(f"{_log_prefix}- Start OCR Preprocessing")
        logger.info(f"{_log_prefix}- OCR PostProcessing Time : {time.time() - start_preproc}")
        return None

class AzureInvoiceOCR(AbstractOCRExtractor):
    def __init__(self):
        """Initialises the class."""
        self.Name = "Azure Invoice OCR"
        self.client = None
        self.form_path = None
        self.text = None
        self._config()

    def _config(self) -> None:
        """Configuration Values."""
        self.endpoint = cfg.models.OCR.Azure_Layout.endpoint + cfg.models.OCR.Azure_Invoice.endpoint
        self.key = cfg.models.OCR.Azure_Layout.Key
        self.headers = {
                # Request headers
                'Content-Type': 'application/octet-stream',
                'Ocp-Apim-Subscription-Key': self.key,
            }

        self.params = {
            "includeTextDetails": True
        }
        return True
    
    def _azure_request(self, filepath, info):
        """Responsible for making the actual request to Azure"""
        with open(filepath, "rb") as f:
            data_bytes = f.read()
        try:
            resp = post(url = self.endpoint, data = data_bytes, headers = self.headers, params = self.params)
            if resp.status_code != 202:
                return None
            get_url = resp.headers["operation-location"]
        except Exception as e:
            raise E.OCRError(info["xxxTrxID"], info["FileIDx"], filepath.split("/")[-1], info["PageIDx"], e)
        return get_url

    def _pole_azure_request(self, req_url):
        """Poles the Azure endpoint for the job status"""
        key = os.environ['AZURE_KEY']
        n_tries = cfg.models.OCR.Azure_Invoice.pole_tries
        wait_sec = cfg.models.OCR.Azure_Invoice.pole_wait_secs
        current_tries = 0
        # 1. Try multiple times until we get response - pole
        for i in range(n_tries):
            try:
                resp = get(url = req_url, headers = {"Ocp-Apim-Subscription-Key": key})
                resp_json = json.loads(resp.text)
                if resp.status_code != 200:
                    return None
                status = resp_json["status"]
                if status == "succeeded":
                    return resp_json
                if status == "failed":
                    return None
                time.sleep(wait_sec)
            except Exception as e:
                raise Exception(e)
        return None
    
    def extract(
        self,
        info:dict,
        image_path: str
    ):
        """Main function call to perform OCR.

        This function call is used to call the OCR functionality.

        Args
        ----
            trxId: The request transaction ID. Used for logging purpose.
            pageIdx: To keep track of the page in multiprocessign scenario.
            fileIdx: To keep track of the file in multiprocessign scenario.
            images_folder: Full path to the images folder to perform OCR.
            postprocess: Boolean value to run postprocess. Default False.
            outfilepath: Full path in case the OCR output needs to be saved.

        Returns
        -------
            The JSON response for the OCR API call.

        Raises
        ------
            AzureJobFailure: In case the OCR job failed.
            AzureJobSubmissionFailure: In case  the job could not be submitted.

        """
        info["OCR"] = self.Name
        _log_prefix = U.set_log_prefix(**info)
        self.image_path = image_path
        try:
            if cfg.models.OCR.Dev_Saver:
                # Search for filename in data folder if found return else follow through
                filename = info["Filename"]
                filename = filename.replace("."+filename.split(".")[-1], "")
                pagename = info['Pagename'].replace(".jpg","")
                ocr_filename = f"{filename}_{pagename}.json"
                data = None
                if os.path.isfile(os.path.join("data/ocr", ocr_filename)):
                    with open(os.path.join("data/ocr", ocr_filename), "r") as f:
                        data = json.loads(f.read())
                if data:
                    logger.info(f"{_log_prefix}- Return Local OCR page")
                    return data
        except Exception as e:
            logger.warn(f"{_log_prefix}- Local document extraction failed - {e}")
        # Local Extraction not possible or present call API
        logger.info(f"{_log_prefix}- Return new OCR page")
        try:
            ocr_start = time.time()
            image_name = image_path.split("/")[-1]
            logger.info(f"{_log_prefix}- Begin OCR for page")
            # 1. send the documents for OCR
            pole_url = self._azure_request(filepath = image_path)
            logger.info(f"{_log_prefix}- OCR pole URL {pole_url}")
            if pole_url is None:
                raise  E.OCRError(info["xxxTrxID"], info["FileIDx"], image_path.split("/")[-1], info["PageIDx"], "Pole URL is None.")
            # 2. Poll the results
            invoice_json = self._pole_azure_request(pole_url)
            ocr_end = time.time()
            logger.info(f"{_log_prefix}- OCR Time : {ocr_end - ocr_start}")
            try:    
                if invoice_json and cfg.models.OCR.Dev_Saver:
                    os.makedirs("data/ocr", exist_ok=True)
                    logger.info(f"{_log_prefix}- Save Local OCR page - {ocr_filename}")
                    with open(os.path.join("data/ocr", ocr_filename), 'w') as f:
                        json.dump(invoice_json, f)
            except Exception as e:
                logger.warn(f"{_log_prefix}- Local document saving failed - {e}")
        except Exception as e:
            raise E.OCRError(info["xxxTrxID"], info["FileIDx"], image_path.split("/")[-1], info["PageIDx"], e)
        return invoice_json
    
    def postprocess(self, info, extract_response) -> str:
        """Extracts all text portion from OCR data.

        The post processing specific logic extracts all the text and returns it
        as a string tot he calling program.

        Args
        ----
            extract_response: The JSON Response from the OCR API call.

        Returns
        -------
            DataFrame: Azure detected tables as pandas dataframe.

        Raises
        ------
            None

        """
        # 1. Get the content for all pages within the document.
        #   - code is written for multiple pages to be generic but in the cbd flow
        #     only one page is sent at a time.
        info["OCR"] = self.Name
        _log_prefix = U.set_log_prefix(**info)
        start_preproc = time.time()
        logger.info(f"{_log_prefix}- Start OCR PostProcessing")
        logger.info(f"{_log_prefix}- OCR PostProcessing Time: {time.time() - start_preproc}")
        return None

