import json
import warnings
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from flask import Flask
from freezegun import freeze_time
from minio import Minio

from storage.minio_util import heartbeat, get_client
from utils.sandbox.enum import StatusType, TestCaseType
from utils.sandbox.util import Task, TestCase
from utils.isolate.util import init_sandbox
from utils.sandbox.inititalize.util import initialize_task, initialize_test_case_to_sandbox
 
# Since "TestCase", "TestCaseType" is start with "Test", so it will be confirm a Test Class by Pytest and raise the warning.
# We need to filter the warning by warnings.filterwarnings.
warnings.filterwarnings("ignore", message="cannot collect test class .+")

BUCKET_NAME = "testcase"
FILE_NAME = ["testcase1.json", "testcase2.json"]
FILE_STRING = [json.dumps(["5 1 2 3 4 5", "4 1 2 3 4"]), json.dumps(["3 1 2 3", "7 1 2 3 4 5 6 7"])]


@pytest.fixture
def storage_client(app: Flask) -> Minio:
    with app.app_context():
        return get_client()


@pytest.fixture
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
    
    for index in range(len(FILE_NAME)):
        with NamedTemporaryFile() as file:
            file.write(FILE_STRING[index].encode("utf-8"))
            file.seek(0)
            assert file.read() == FILE_STRING[index].encode("utf-8")
            storage_client.fput_object(BUCKET_NAME, FILE_NAME[index], file.name)


def _delete_the_file(app: Flask, storage_client: Minio) -> None:
    with app.app_context():
        assert heartbeat()

    if not storage_client.bucket_exists(BUCKET_NAME):
        return

    for index in range(len(FILE_NAME)):
        storage_client.remove_object(BUCKET_NAME, FILE_NAME[index])
    
    for index in range(len(FILE_NAME)):
        with pytest.raises(Exception):
            storage_client.stat_object(BUCKET_NAME, FILE_NAME[index])

 
class TestInitializeTask:
    def test_with_test_task_should_modify_the_state_of_task(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
        
        assert test_task.status == StatusType.INITIAL

    def test_with_test_task_should_create_the_sandbox(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
        
        assert Path("/var/local/lib/isolate/0").exists()
    
    @freeze_time("2002-06-25 00:00:00")
    def test_with_test_task_should_create_flow_to_result(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
        
        assert test_task.flow["init_code"] == "2002-06-25 00:00:00"
        assert test_task.flow["init_solution"] == "2002-06-25 00:00:00"
        assert test_task.flow["init_checker"] == "2002-06-25 00:00:00"

    def test_with_test_task_without_user_code_should_not_create_user_file(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        test_task.user_code = None
        with app.app_context():

            initialize_task(test_task, 0)
        
        assert not Path("/var/local/lib/isolate/0/box/submit_code.cpp").exists()

    def test_with_test_task_without_solution_code_should_not_create_solution_file(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        test_task.solution_code = None
        with app.app_context():

            initialize_task(test_task, 0)
        
        assert not Path("/var/local/lib/isolate/0/box/solution.cpp").exists()

    def test_with_test_task_without_checker_code_should_not_create_user_file(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        test_task.checker_code = None
        with app.app_context():

            initialize_task(test_task, 0)
        
        assert not Path("/var/local/lib/isolate/0/box/checker.cpp").exists()

    def test_with_test_task_should_place_the_correct_code_in_task_to_sandbox(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
        
        assert Path("/var/local/lib/isolate/0/box/submit.cpp").exists()
        assert Path("/var/local/lib/isolate/0/box/submit.cpp").read_text() == test_task.user_code.code
        assert Path("/var/local/lib/isolate/0/box/solution.cpp").exists()
        assert Path("/var/local/lib/isolate/0/box/solution.cpp").read_text() == test_task.solution_code.code
        assert Path("/var/local/lib/isolate/0/box/checker.cpp").exists()
        assert Path("/var/local/lib/isolate/0/box/checker.cpp").read_text() == test_task.checker_code.code
        assert Path("/var/local/lib/isolate/0/box/testlib.h").exists()

class TestInitializeTestCase:
    def test_with_plain_text_test_case_should_place_the_test_case_to_sandbox(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            init_sandbox(0)
        
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
        
        assert Path("/var/local/lib/isolate/0/box/1.in").exists()
        assert Path("/var/local/lib/isolate/0/box/2.in").exists()

    def test_with_static_file_test_case_should_place_the_test_case_to_sandbox(self, app: Flask, cleanup_test_sandbox: None, setup_static_file_test_case: None, test_task: Task):
        test_task.test_case = [TestCase(TestCaseType.STATIC_FILE.value, "file1.test"), TestCase(TestCaseType.STATIC_FILE.value, "file2.test")]
        with app.app_context():
            init_sandbox(0)
        
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            assert Path("/var/local/lib/isolate/0/box/1.in").exists()
            assert Path("/var/local/lib/isolate/0/box/2.in").exists()
            assert Path("/var/local/lib/isolate/0/box/3.in").exists()
            assert Path("/var/local/lib/isolate/0/box/4.in").exists()

    def test_with_fetch_file_from_storage_server_should_place_the_test_case_to_sandbox(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, place_the_file: None):
        test_task.test_case = [TestCase(TestCaseType.STATIC_FILE.value, "testcase1.json"), TestCase(TestCaseType.STATIC_FILE.value, "testcase2.json")]
        with app.app_context():
            init_sandbox(0)
        
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            assert Path("/var/local/lib/isolate/0/box/1.in").exists()
            assert Path("/var/local/lib/isolate/0/box/2.in").exists()
            assert Path("/var/local/lib/isolate/0/box/3.in").exists()
            assert Path("/var/local/lib/isolate/0/box/4.in").exists()

    def test_with_fetch_unavailable_file_from_storage_server_should_place_the_test_case_to_sandbox(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        test_task.test_case = [TestCase(TestCaseType.STATIC_FILE.value, "testcase1.json"), TestCase(TestCaseType.STATIC_FILE.value, "testcase2.json")]
        with app.app_context():
            init_sandbox(0)
        
            with pytest.raises(AssertionError):
                initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
