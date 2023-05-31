import os
from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Final

from flask import Flask
from minio import Minio
from pytest import MonkeyPatch, fixture, raises

import storage.minio_util
from storage.minio_util import download, heartbeat, get_client


BUCKET_NAME: Final[str] = "testcase"
FILE_NAME: Final[str] = "test_file"
FILE_STRING: Final[str] = "test_string"


@fixture
def storage_client(app: Flask) -> Minio:
    with app.app_context():
        return get_client()


@fixture
def place_the_file(app: Flask, storage_client: Minio) -> None:
    _delete_the_file(app, storage_client)
    _upload_the_file(app, storage_client)

    yield

    _delete_the_file(app, storage_client)


def _upload_the_file(app: Flask, storage_client: Minio) -> None:
    with app.app_context():
        assert heartbeat()

    if not storage_client.bucket_exists(BUCKET_NAME):
        storage_client.make_bucket(BUCKET_NAME)
    
    with NamedTemporaryFile() as file:
        file.write(FILE_STRING.encode("utf-8"))
        file.seek(0)
        assert file.read() == FILE_STRING.encode("utf-8")
        storage_client.fput_object(BUCKET_NAME, FILE_NAME, file.name)
    
def _delete_the_file(app: Flask, storage_client: Minio) -> None:
    with app.app_context():
        assert heartbeat()

    storage_client.remove_object(BUCKET_NAME, FILE_NAME)
    
    with raises(Exception):
        storage_client.stat_object(BUCKET_NAME, FILE_NAME)


class TestMinIOStorage:
    def test_heartbeat_should_return_true(self, app: Flask):
        with app.app_context():
            
            assert heartbeat()

    def test_heartbeat_with_wrong_secret_should_return_false(self, app: Flask, monkeypatch: MonkeyPatch):
        modified_environ: dict[str, str] = os.environ.copy()
        modified_environ["MINIO_SECRET_KEY"] = "WRONG_SECRET_KEY"
        monkeypatch.setattr(storage.minio_util, "environ", modified_environ)
        with app.app_context():

            assert not heartbeat()

    def test_download_file_with_no_heart_beat_should_revert_the_action(self, app: Flask, monkeypatch: MonkeyPatch):
        modified_environ: dict[str, str] = os.environ.copy()
        modified_environ["MINIO_SECRET_KEY"] = "WRONG_SECRET_KEY"
        monkeypatch.setattr(storage.minio_util, "environ", modified_environ)
        with app.app_context():
            with TemporaryDirectory() as temp_dir:

                with raises(Exception):
                    download(BUCKET_NAME, FILE_NAME, Path(temp_dir) / FILE_NAME)    

    def test_download_file_from_storage_server_should_got_the_file(self, app: Flask, storage_client: Minio, place_the_file: None):
        with app.app_context():
            with TemporaryDirectory() as temp_dir:

                download(BUCKET_NAME, FILE_NAME, Path(temp_dir) / FILE_NAME)

                with open(Path(temp_dir) / FILE_NAME, "r") as file:
                    assert file.read() == FILE_STRING