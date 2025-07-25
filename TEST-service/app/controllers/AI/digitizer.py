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


class DigitizerModel:
    def __init__(self):
        self.url = cfg.models.Digitizer.url.v1

    def Digitize(self, image_path: str, ocr_data, info: dict):
        url = self.url + "?trxId=" + str(info["xxxTrxID"]) + "&pageId=" + str(info["PageIDx"])
        payload = {"ocr": json.dumps(ocr_data)}
        files = {"file": open(image_path, "rb")}
        headers = {"Accept": "application/json"}
        try:
            response = requests.post(url, files=files, headers=headers, data=payload)
        except Exception as e:
            raise E.ExtractorJobFailure(info["xxxTrxID"], info["FileIDx"], info["PageIDx"], e)
        return response.json()
