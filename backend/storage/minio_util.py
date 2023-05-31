from os import environ
from traceback import format_exc
from typing import Final

from flask import current_app
from loguru import logger
from minio import Minio

from setting.util import Setting


def get_client() -> Minio:
    setting: Setting = current_app.config["setting"]

    ACCESS_KEY: Final[str] = environ.get("MINIO_ACCESS_KEY")
    SECRET_KEY: Final[str] = environ.get("MINIO_SECRET_KEY")
    ENDPOINT: Final[str] = setting.minio.endpoint

    client = Minio(endpoint=ENDPOINT, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

    return client


def heartbeat() -> bool:
    client: Minio = get_client()

    try:
        client.bucket_exists("notexistbucket")
        return True
    except:
        print(format_exc())
        return False


def download(bucket_name: str, object_name: str, file_name: str) -> None:
    assert heartbeat()
    
    client: Minio = get_client()

    client.fget_object(bucket_name, object_name, file_name)

    logger.info(f"Fetch the file {object_name} from {bucket_name}.")