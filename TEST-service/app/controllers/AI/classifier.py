#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import json
import requests

from app.core.config import cfg
from app.utils import utilities as U
from app.utils import exceptions as E


class ClassifierModel:
    def __init__(self):
        self.url = cfg.models.Classifier.url.v1

    def Classify(self, image_path: str, ocr_data, info: dict):
        image_name = image_path.split("/")[-1]
        ext = image_name.split(".")[-1]
        ocr_bytes = json.dumps(ocr_data).encode("utf-8")
        files = {"file": open(image_path, "rb")}
        headers = {"Accept": "application/json"}
        payloads = {
            "annotations": ocr_bytes,
        }

        url = f"{cfg.models.Classifier.url.v1}?trxId={info['xxxTrxID']}&pageId={info['PageIDx']}"

        try:
            response = requests.post(url, files=files, headers=headers, data=payloads)
        except Exception as e:
            raise E.ModelJobFailure(info["xxxTrxID"], info["FileIDx"], info["PageIDx"], e)
        return response.json()
