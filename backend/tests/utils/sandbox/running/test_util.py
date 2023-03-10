from freezegun import freeze_time

from utils.sandbox.enum import ExecuteType, StatusType
from utils.sandbox.inititalize.util import initialize_task, initialize_test_case_to_sandbox
from utils.sandbox.running.util import run_task
from utils.sandbox.util import Task

def test_with_test_task_should_change_the_task_status(cleanup_test_sandbox: None, test_task: Task):
    run_task(test_task, test_task.test_case, 0)
    
    assert test_task.status == StatusType.RUNNING

@freeze_time("2002-06-25 00:00:00")
def test_with_test_task_should_have_running_timestamp(cleanup_test_sandbox: None, test_task: Task):
    run_task(test_task, test_task.test_case, 0)
    
    assert test_task.flow["running"] == "2002-06-25 00:00:00"

def test_compile_with_test_task_should_return_result(cleanup_test_sandbox: None, test_task: Task):
    test_task.execute_type = ExecuteType.COMPILE.value
    initialize_task(test_task, 0)
    
    run_task(test_task, test_task.test_case, 0)
    
    assert "exitcode" in test_task.result
    assert int(test_task.result["exitcode"]) == 0

def test_execute_with_test_task_should_return_result(cleanup_test_sandbox: None, test_task: Task):
    test_task.execute_type = ExecuteType.EXECUTE.value
    initialize_task(test_task, 0)
    initialize_test_case_to_sandbox(test_task.test_case, 0)
    
    run_task(test_task, test_task.test_case, 0)
    
    assert int(test_task.result["compile"]["exitcode"]) == 0
    assert int(test_task.result["report"][0]["exitcode"]) == 0

def test_judge_with_test_task_should_return_result(cleanup_test_sandbox: None, test_task: Task):
    initialize_task(test_task, 0)
    initialize_test_case_to_sandbox(test_task.test_case, 0)
    
    run_task(test_task, test_task.test_case, 0)
    
    assert int(test_task.result["compile"]["user_code"]["exitcode"]) == 0
    assert int(test_task.result["compile"]["solution_code"]["exitcode"]) == 0
    assert int(test_task.result["compile"]["checker_code"]["exitcode"]) == 0
    assert test_task.result["judge"]["report"][0]["verdict"] == "AC"
    assert test_task.result["judge"]["report"][1]["verdict"] == "AC"

def test_with_invalid_execute_type_should_return_error_result(cleanup_test_sandbox: None, test_task: Task):
    test_task.execute_type = "Invalid_type"
    initialize_task(test_task, 0)
    initialize_test_case_to_sandbox(test_task.test_case, 0)
    
    run_task(test_task, test_task.test_case, 0)
    
    assert test_task.result["error"] == "Invalid execute type."
