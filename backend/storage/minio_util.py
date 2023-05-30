from os import environ
from traceback import format_exc
from typing import Final

from minio import Minio
from flask import current_app

from setting.util import Setting


def heartbeat() -> bool:
    setting: Setting = current_app.config["setting"]
    
    ACCESS_KEY: Final[str] = environ.get("MINIO_ACCESS_KEY")
    SECRET_KEY: Final[str] = environ.get("MINIO_SECRET_KEY")
    ENDPOINT: Final[str] = setting.minio.endpoint

    client = Minio(endpoint=ENDPOINT, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

    try:
        print(format_exc())
        client.bucket_exists("notexistbucket")
        return True
    except:
        return False