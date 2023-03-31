import json
from tempfile import mkdtemp
from pathlib import Path
from shutil import rmtree

import pytest
from flask import Flask

from app import create_app
from utils.sandbox.util import CodePackage, Option, Task, TestCase
from utils.isolate.util import cleanup_sandbox
from utils.sandbox.enum import ExecuteType
from setting.util import Setting, SettingBuilder


@pytest.fixture
def checker_code() -> str:
    with open("./tests/test_code/checker.cpp") as file:
        return file.read()

@pytest.fixture
def user_code() -> str:
    with open("./tests/test_code/code.cpp") as file:
        return file.read()

@pytest.fixture
def wrong_syntax_code() -> str:
    with open("./tests/test_code/wrong_syntax_code.cpp") as file:
        return file.read()
    
@pytest.fixture
def runtime_error_code() -> str:
    with open("./tests/test_code/runtime_error_code.cpp") as file:
        return file.read()

@pytest.fixture
def timeout_code() -> str:
    with open("./tests/test_code/timed_out_code.cpp") as file:
        return file.read()

@pytest.fixture
def testlib() -> str:
    with open("testlib.h") as file:
        return file.read()

@pytest.fixture()
def app():
    storage_path: str = mkdtemp()
    app = create_app({"STORAGE_PATH": storage_path})
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


@pytest.fixture
def cleanup_test_sandbox():
    cleanup_sandbox(0)


@pytest.fixture
def setup_static_file_test_case(app: Flask) -> None:
    storage_path: str = app.config["STORAGE_PATH"]
    with open(Path(storage_path) / "testcase/file1.test.json", "w") as file:
        file.write(json.dumps(["5", "6"]))
    with open(Path(storage_path) / "testcase/file2.test.json", "w") as file:
        file.write(json.dumps(["7", "8"]))


@pytest.fixture()
def test_task(checker_code: str, user_code: str):
    return Task(
        checker_code=CodePackage(code=checker_code, compiler="cpp"),
        solution_code=CodePackage(code=user_code, compiler="cpp"),
        user_code=CodePackage(code=user_code, compiler="cpp"),
        execute_type=ExecuteType.JUDGE.value,
        options=Option(
            threading=False,
            time=2.5,
            wall_time=2.5,
        ),
        test_case=[
            TestCase(type="plain-text", value="5"),
            TestCase(type="plain-text", value="6"),
        ],
    )


def _create_storage_folder(storage_path: str):
    (Path(storage_path) / "result").mkdir()
    (Path(storage_path) / "submission").mkdir()
    (Path(storage_path) / "testcase").mkdir()
