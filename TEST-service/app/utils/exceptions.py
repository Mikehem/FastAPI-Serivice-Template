#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
_INVALID_FILETYPE = "Invalid File Type, expected pdf, jpeg, jpg"
_MULTIPLE_FILETYPE = "Multiple File Types found, expected pdf, jpeg, jpg"
_AZURE_JOB_SUBMIT_FAILURE = "Failed to submit azure ocr job for page."
_AZURE_JOB_FAILURE = "Azure OCR job failed for page."
_CLASSIFIER_JOB_FAILURE = "Failed to classifiy page."
_EXTRACTOR_JOB_FAILURE = "Failed to extract page."
_OCR_ERROR = "Failed to perform OCR."
_REF_DATA_FIND_ERROR = "Item not found in refrence data store."
_PROCESSING_ERROR = "Error processing the document."
_DB_JOB_ERROR = "Issue with saving lab extraction in database."
_INVALID_REQUEST_INFO = "Invalid Request Info."
_INVALID_PROCESS_CONTROL = "Invalid Process Control."
_JWT_DECODE_ERROR = "Failed to decode JWT Token."
_CLIENT_NOT_FOUND = "Client not found."
_INVALID_CLIENT_INFO = "Invalid Client Info."
_MULTIPLE_PDF_FILES = "Multiple PDF files found in the request."


class OCRError(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, fileId, pageId, message=_OCR_ERROR):
        """Initialises the class."""
        self.trxid = trxid
        self.fileId = fileId
        self.pageId = pageId
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[{self.trxid}] [Filename/Fileid/PageId: {self.fileId}/{self.pageId}] -> {self.message}"


class InvalidFileType(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, filename, message=_INVALID_FILETYPE):
        """Initialises the class."""
        self.trxid = trxid
        self.filename = filename
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[Filename: {self.filename}] -> {self.message}"


class MultipleTypesFound(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, filetypes, message=_MULTIPLE_FILETYPE):
        """Initialises the class."""
        self.trxid = trxid
        self.filetypes = filetypes
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"{self.trxid}:[File Types: {self.filetypes}] -> {self.message}"


class MultiplePDFFiles(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, filetypes, message=_MULTIPLE_PDF_FILES):
        """Initialises the class."""
        self.trxid = trxid
        self.filetypes = filetypes
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"{self.trxid}:[File Types: {self.filetypes}] -> {self.message}"


class AzureJobSubmissionFailure(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, pageid, api_response, message=_AZURE_JOB_SUBMIT_FAILURE):
        """Initialises the class."""
        self.trxid = trxid
        self.pageid = pageid
        self.message = message
        self.api_response = api_response
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[{self.trxid}] {self.pageid} -> {self.message} => {self.api_response}"


class AzureJobFailure(Exception):
    """xxx LRD Defined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, fileIdx, pageid, api_response, message=_AZURE_JOB_FAILURE):
        """Initialises the class."""
        self.trxid = trxid
        self.fileId = fileIdx
        self.pageid = pageid
        self.message = message
        self.api_response = api_response
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[TrxID: {self.trxid}] [File/Page: {self.fileId}/{self.pageid}] -> Msg: {self.message} => API Response: {self.api_response}"


class ModelJobFailure(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, fileIdx, pageid, api_response, message=_CLASSIFIER_JOB_FAILURE):
        """Initialises the class."""
        self.trxid = trxid
        self.fileId = fileIdx
        self.pageid = pageid
        self.message = message
        self.api_response = api_response
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[TrxID: {self.trxid}] [File/Page: {self.fileId}/{self.pageid}] -> Msg: {self.message} => API Response: {self.api_response}"


class ExtractorJobFailure(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, fileIdx, pageid, api_response, message=_EXTRACTOR_JOB_FAILURE):
        """Initialises the class."""
        self.trxid = trxid
        self.fileId = fileIdx
        self.pageid = pageid
        self.message = message
        self.api_response = api_response
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[TrxID: {self.trxid}] [File/Page: {self.fileId}/{self.pageid}] -> Msg: {self.message} => API Response: {self.api_response}"


class ReferenceDataNotFound(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, find_key, message=_REF_DATA_FIND_ERROR):
        """Initialises the class."""
        self.message = message
        self.find_key = find_key
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"Msg: {self.message} => Key: {self.find_key}"


class ProcessingError(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, message=_PROCESSING_ERROR, value: dict = None):
        """Initialises the class."""
        self.value = value
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"Msg: {self.message} => {self.value}"


class DBJobError(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, message=_DB_JOB_ERROR, value: dict = None):
        """Initialises the class."""
        self.value = value
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"Msg: {self.message} => {self.value}"


class InvalidRequestInfo(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, request_info, message=_INVALID_REQUEST_INFO):
        """Initialises the class."""
        self.requset_info = request_info
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[Request Info: {self.requset_info}] -> {self.message}"


class InvalidClientInfo(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, client_info, message=_INVALID_CLIENT_INFO):
        """Initialises the class."""
        self.client_info = client_info
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[Request Info: {self.client_info}] -> {self.message}"


class InvalidProcessInfo(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, trxid, process_info, message=_INVALID_PROCESS_CONTROL):
        """Initialises the class."""
        self.trxid = trxid
        self.process_info = process_info
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"{self.trxid}: [Process Info: {self.process_info}] -> {self.message}"


class JWTDecodeError(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, message=_JWT_DECODE_ERROR):
        """Initialises the class."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"{self.message}"


class ClientNotFound(Exception):
    """xxx LRD DEfined Custom Exceptions.

    This provides a suite of custom exceptions.

    Typical usage example:

    result = exceptions._specif_Exception(parameters)
    """

    def __init__(self, client_id, message=_CLIENT_NOT_FOUND):
        """Initialises the class."""
        self.message = message
        self.client_id = client_id
        super().__init__(self.message)

    def __str__(self):
        """Print or string formatter."""
        return f"[Client ID: {self.client_id}] -> {self.message}"
