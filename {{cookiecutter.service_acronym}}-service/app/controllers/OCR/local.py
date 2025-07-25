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

import pytesseract
from pytesseract import Output

from app.utils import exceptions as E
from app.controllers.OCR.abstract_ocr import AbstractOCRExtractor
from app.core.config import cfg

class pyTesseractOCR(AbstractOCRExtractor):
    def __init__(self):
        """Initialises the class."""
        self.client = None
        self.form_path = None
        self.text = None
        self._config()

    def _config(self) -> None:
        """Configuration Values."""
        return None

    def extract(
        self,
        trxId: str,
        pageIdx: str,
        fileIdx: str,
        image_path: str,
        postprocess: bool = True,
        outfilepath: str = None,
    ) -> str:
        """Main function call to perform OCR.

        This function call is used to call the OCR functionality.

        Args
        ----
            trxId: The request transaction ID. Used for logging purpose.
            pageIdx: To keep track of the page in multiprocessign scenario.
            fileIdx: To keep track of the file in multiprocessign scenario.
            image_path: Full path to the image to perform OCR.
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
        try:
            # tesseract needs the right channel order
            # cropped_rgb = cv2.cvtColor(imageBytes, cv2.COLOR_BGR2RGB)

            # give the numpy array directly to pytesseract, no PIL or other acrobatics necessary
            # Results = pytesseract.image_to_string(cropped_rgb, lang="eng")
            # img_tesseract = Image.fromarray(imageBytes)
            # print("***********",image_path)
            # image_bytes = bytearray(utilities.read_image_bin(image_path))
            response = pytesseract.image_to_data(image_path, output_type=Output.DICT)
            # save the response json as file
            if outfilepath:
                with open(outfilepath, "w") as f:
                    json.dump(response, f)
            else:
                pass
            # postprocess the response to extract only text
            if postprocess:
                self.text = self.postprocess(extract_response=response)
            else:
                self.text = response
        except Exception as e:
            raise E.OCRError(trxId, fileIdx, image_path.split("/")[-1], pageIdx, e)
        return self.text

    def postprocess(self, extract_response) -> str:
        """Extracts all text portion from OCR data.

        The post processing specific logic extracts all the text and returns it
        as a string tot he calling program.

        Args
        ----
            extract_response: The JSON Response from the OCR API call.

        Returns
        -------
            raw text concatenated intoa single string object.

        Raises
        ------
            None

        """
        rawText = " ".join(extract_response["text"])
        return rawText
