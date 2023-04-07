import warnings
from pathlib import Path

import pytest
from flask import Flask
from freezegun import freeze_time

from utils.sandbox.enum import StatusType, TestCaseType
from utils.sandbox.util import Task, TestCase
from utils.isolate.util import init_sandbox
from utils.sandbox.inititalize.util import initialize_task, initialize_test_case_to_sandbox
 
# Since "TestCase", "TestCaseType" is start with "Test", so it will be confirm a Test Class by Pytest and raise the warning.
# We need to filter the warning by warnings.filterwarnings.
warnings.filterwarnings("ignore", message="cannot collect test class .+")
 
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
        init_sandbox(0)
        
        with app.app_context():
            initialize_test_case_to_sandbox(test_task.test_case, 0)
        
        assert Path("/var/local/lib/isolate/0/box/1.in").exists()
        assert Path("/var/local/lib/isolate/0/box/2.in").exists()

    def test_with_static_file_test_case_should_place_the_test_case_to_sandbox(self, app: Flask, cleanup_test_sandbox: None, setup_static_file_test_case: None, test_task: Task):
        init_sandbox(0)
        test_task.test_case = [TestCase(TestCaseType.STATIC_FILE.value, "file1.test"), TestCase(TestCaseType.STATIC_FILE.value, "file2.test")]
        with app.app_context():
        
            initialize_test_case_to_sandbox(test_task.test_case, 0)
            
            assert Path("/var/local/lib/isolate/0/box/1.in").exists()
            assert Path("/var/local/lib/isolate/0/box/2.in").exists()
            assert Path("/var/local/lib/isolate/0/box/3.in").exists()
            assert Path("/var/local/lib/isolate/0/box/4.in").exists()
