import os
import boto3
import botocore
import glob


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
