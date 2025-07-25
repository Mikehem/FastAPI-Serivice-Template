# noqa
import os
from app.utils.datastore import downloadDirectoryFromS3
from dotenv import load_dotenv

os.makedirs("logs", exist_ok=True)
load_dotenv()