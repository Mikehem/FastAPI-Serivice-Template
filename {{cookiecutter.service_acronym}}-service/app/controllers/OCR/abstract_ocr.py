#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
"""Abstract Class for OCR implementations.

LSet this abstract class to ensure that all OCR implementations,
follow the secified implementations. This ensures minimum change 
in code, restricting changes to a configuration.

  Typical usage example:
  
  class OCRType(AbstractOCRExtractor)
"""
from abc import ABC, abstractmethod


class AbstractOCRExtractor(ABC):
    def __init__(self, ocr_name: str):
        """Initialises the class."""
        self.ocr_name = ocr_name

    @abstractmethod
    def _config(self):
        pass

    @abstractmethod
    def postprocess(self, extract_response):
        pass

    @abstractmethod
    def extract(
        self,
        trxId: str,
        pageIdx: str,
        fileIdx: str,
        image_path: str,
        postprocess: bool = True,
        outfilepath: str = None,
        json_response_path = None
    ):
        pass
