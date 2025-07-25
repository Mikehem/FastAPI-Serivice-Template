#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import os
import boto3
import botocore
import glob
import json
import shutil

import app.utils.constants as C

# from xxxai.datastore.AWS.S3.dao import DAO

from datetime import datetime, timezone
from app.controllers.OCR.azure import AzureInvoiceOCR, AzureLayoutOCR

global g_ocr
g_ocr = None


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def transform_to_utc_datetime(dt: datetime) -> datetime:
    return dt.astimezone(tz=timezone.utc)


def read_image_bin(img_path):
    """Reads an image and converts to binary format."""
    with open(img_path, "rb") as file:
        file_data = file.read()
    return file_data


def get_file_details_from_name(filepath: str):
    """Get the file details from the url."""
    if "s3://" in filepath.lower():
        file_type = "S3"
    elif "local://" in filepath.lower():
        file_type = "local"
    elif "http://" in filepath.lower():
        file_type = "http"
    elif "https://" in filepath.lower():
        file_type = "https"
    else:
        file_type = "unknown"
    #
    filename = filepath.split("/")[-1]
    filedir = filepath.replace(filename, "")
    if filedir.endswith("/"):
        filedir = filedir[:-1]
    return filename, filedir, file_type


def get_file_type(filepath: str):
    if ".pdf" in filepath.lower():
        return "pdf"
    elif ".jpg" in filepath.lower():
        return "jpg"
    elif ".jpeg" in filepath.lower():
        return "jpeg"


def get_file_content_type(filepath: str):
    if ".pdf" in filepath.lower():
        return "application/pdf"
    elif ".jpg" in filepath.lower():
        return "image/jpeg"
    elif ".jpeg" in filepath.lower():
        return "image/jpeg"


def get_file_name(filepath: str):
    """Get the file name from the url."""
    filename = filepath.split("/")[-1]
    return filename


def check_standard_file_type(file_name: str):
    """Check if the file types are standard file types

    Args:
        file_name (str): file name

    Returns:
        bool: True if all file types are standard file types
    """
    file_mime_type = file_name.split(".")[-1]
    if file_mime_type in C.STANDARD_FILE_TYPES:
        return file_name, True
    return file_name, False


def prepend_msg(txn_id: str):
    """Formats a string for logger."""
    return f"[TRX-Id:{txn_id}]"


def set_log_prefix(**kwargs):
    msg = ""
    for key, value in kwargs.items():
        if value is None:
            continue
        msg = msg + f"[{key}: {value}]"
    return msg


def build_store_path(cfg, postfix: str = None):
    """Builds the store path based on the object store type."""
    if "s3://" in postfix.lower():
        return postfix
    obj_store_type = cfg.store.Object_Store.default
    if "S3" == obj_store_type:
        bucket = cfg.store.Object_Store.S3.Bucket
        if postfix:
            return f"s3://{bucket}/{postfix}"
        else:
            return f"s3://{bucket}/"
    elif "Local" == obj_store_type:
        if postfix:
            return f"local://{cfg.store.Object_Store.Local.Path_Prefix}/{postfix}/"
        else:
            return f"local://{cfg.store.Object_Store.Local.Path_Prefix}/"
    else:
        return None


def get_bucket_name(s3_path: str):
    """Get the bucket name from the s3 path."""
    if "s3://" in s3_path.lower():
        bucket_name = s3_path.split("/")[2]
    else:
        bucket_name = None
    return bucket_name


def get_file_path(s3_path: str):
    """Get the file path from the s3 path."""
    if "s3://" in s3_path.lower():
        # s3://bucket_name/file_path1/file_path2
        file_path = "/".join(s3_path.split("/")[3:])
    else:
        file_path = None
    return file_path


def upload_file(cfg, local_path: str, remote_path: str):
    obj_store_type = cfg.store.Object_Store.default
    if "S3" == obj_store_type:
        bucket = cfg.store.Object_Store.S3.Bucket
        Access_Key = cfg.store.Object_Store.S3.Access_Key
        Secret_Key = cfg.store.Object_Store.S3.Secret_Key
        s3_dao = DAO(bucket, Access_Key, Secret_Key)
        s3_dao.upload_file_to_s3(local_path, remote_path)
    elif "Local" == obj_store_type:
        remote_path_prefix = cfg.store.Object_Store.Local.Path_Prefix
        os.makedirs(remote_path, exist_ok=True)
        shutil.copy(local_path, remote_path)
    else:
        raise ("Invalid Object store default provide - ", obj_store_type)
    return True


def upload_file_to_s3(cfg, local_path: str, s3_path: str):
    obj_store_type = cfg.store.Object_Store.default
    if "S3" == obj_store_type:
        bucket = cfg.store.Object_Store.S3.Bucket
        Access_Key = cfg.store.Object_Store.S3.Access_Key
        Secret_Key = cfg.store.Object_Store.S3.Secret_Key
        s3_dao = DAO(bucket, Access_Key, Secret_Key)
        s3_dao.upload_file_to_s3(local_path, s3_path)
    else:
        raise ("Invalid Object store default provide - ", obj_store_type)
    return True


def downloadDirectoryFromS3_V1(bucketName: str, remoteDirectoryName: str = "conf", localDirectoryRoot="app"):
    session = boto3.Session(
        aws_access_key_id=os.environ["CFG_KEY"],
        aws_secret_access_key=os.environ["CFG_SECRET"],
    )
    s3 = session.resource("s3")
    bucket = s3.Bucket(bucketName)
    print("=======Current Working Directory:", os.getcwd())
    for obj in bucket.objects.filter(Prefix=remoteDirectoryName):
        print("###### obj:", obj.key)
        dir_name = os.path.join(localDirectoryRoot, os.path.dirname(obj.key))
        os.makedirs(dir_name, exist_ok=True)
        bucket.download_file(obj.key, os.path.join(localDirectoryRoot, obj.key))
    return True


def get_OCR(cfg):
    """Sets/Gets the OCR objects for processing at a global level."""
    global g_ocr
    if g_ocr is None:
        g_ocr = {
            "azure_layout": AzureLayoutOCR(),
            "azure_invoice": AzureInvoiceOCR(),
        }
    return g_ocr


def dertermine_ocr(cfg, model: str):
    """Determines the OCR.

    Based on provided model type the method returns
    the specific OCR Object Class

    Args
    ----
        cfg: OmegaConf configuration
        model: String value of choice - Classifier or Extractor

    Returns
    -------
        OCR Object Class instantiated.

    Raises
    ------
        None

    """
    if cfg.models[model].OCR:
        return get_OCR(cfg)[cfg.models[model].OCR]
    return get_OCR(cfg)[cfg.models.OCR.default]


def downloadDirectoryFromS3(bucketName: str, remoteDirectoryName: str = "conf", localDirectoryRoot: str = "app"):
    session = boto3.Session(
        aws_access_key_id=os.getenv("CFG_KEY"),
        aws_secret_access_key=os.getenv("CFG_SECRET"),
    )
    s3 = session.resource("s3")
    bucket = s3.Bucket(bucketName)
    print("=======Directory:", remoteDirectoryName)
    print("Local directory", f"{os.getcwd()}/{localDirectoryRoot}/{remoteDirectoryName}")
    print("Local directry present:", os.path.isdir(f"{os.getcwd()}/{localDirectoryRoot}/{remoteDirectoryName}"))
    # Check for current version
    if os.path.isdir(f"{os.getcwd()}/{localDirectoryRoot}/{remoteDirectoryName}"):
        files = glob.glob(f"{os.getcwd()}/{localDirectoryRoot}/{remoteDirectoryName}/*.ver")
        print(f"---->Local version file [{len(files)}]:", files)
        if len(files) == 1:
            # get the current local version and check if S3 is matching
            print("---->Local version:", files[0].split("/")[-1])
            local_version = files[0].split("/")[-1]
            try:
                s3.Object(bucketName, f"{remoteDirectoryName}/{local_version}").load()
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    print(f"---->Remote version Different From Local - Refresh required")
                    # The object does not exist hence assume new version.
                    # delete the local version file and let the new version take its place
                    os.remove(files[0])
                    for obj in bucket.objects.filter(Prefix=remoteDirectoryName):
                        print("###### obj:", obj.key)
                        dir_name = os.path.join(localDirectoryRoot, os.path.dirname(obj.key))
                        os.makedirs(dir_name, exist_ok=True)
                        bucket.download_file(obj.key, os.path.join(localDirectoryRoot, obj.key))
                else:
                    # Something else has gone wrong.
                    raise Exception(f"{remoteDirectoryName} Loading error...")
            # the version already is uptodate do nothing
            print(f"----->No new {remoteDirectoryName} update.")
        elif len(files) > 1:
            raise Exception(f"{remoteDirectoryName} corruption. More than 1 version file found...")
        else:
            print(f"---->New setup - Download required")
            for obj in bucket.objects.filter(Prefix=remoteDirectoryName):
                print("###### obj:", obj.key)
                dir_name = os.path.join(localDirectoryRoot, os.path.dirname(obj.key))
                os.makedirs(dir_name, exist_ok=True)
                bucket.download_file(obj.key, os.path.join(localDirectoryRoot, obj.key))
    else:
        print(f"---->New setup no local folder - Download required")
        for obj in bucket.objects.filter(Prefix=remoteDirectoryName):
            print("###### obj:", obj.key)
            dir_name = os.path.join(localDirectoryRoot, os.path.dirname(obj.key))
            os.makedirs(dir_name, exist_ok=True)
            bucket.download_file(obj.key, os.path.join(localDirectoryRoot, obj.key))
    return True
