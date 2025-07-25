#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
from app.utils import exceptions as E
from fastapi import UploadFile

_ALLOWED_FILES = ["pdf", "jpeg", "jpg"]


def validate_filetype(trxId: str, fileObj: UploadFile) -> bool:
    """Validates each request input file."""
    # Validate filetype is allowed
    filename = fileObj.filename
    if filename.split(".")[-1].lower() not in _ALLOWED_FILES:

        raise E.InvalidFileType(trxId, fileObj.filename)
    return True
