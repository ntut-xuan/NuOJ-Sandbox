import os
from copy import deepcopy
from flask import Flask
from pytest import MonkeyPatch

import storage.minio_util
from storage.minio_util import heartbeat


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