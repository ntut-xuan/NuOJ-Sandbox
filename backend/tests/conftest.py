from tempfile import mkdtemp
from pathlib import Path
from shutil import rmtree

import pytest

from app import create_app
from setting.util import Setting, SettingBuilder

@pytest.fixture()
def app():
    storage_path: str = mkdtemp()
    app = create_app(
        {
            "STORAGE_PATH": storage_path
        }
    )
    
    with app.app_context():
        app.config["setting"] = SettingBuilder().from_mapping({"sandbox_number": 1})
        _create_storage_folder(storage_path)
        
    # other setup can go here

    yield app

    # clean up / reset resources here
    rmtree(storage_path)


@pytest.fixture()
def client(app):
    return app.test_client()

def _create_storage_folder(storage_path: str):
    (Path(storage_path) / "result").mkdir()
    (Path(storage_path) / "submission").mkdir()
    (Path(storage_path) / "testcase").mkdir()
