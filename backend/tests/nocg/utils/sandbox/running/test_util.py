import json

import pytest
from freezegun import freeze_time
from flask import Flask

from utils.sandbox.enum import ExecuteType, StatusType
from utils.sandbox.inititalize.util import initialize_task, initialize_test_case_to_sandbox
from utils.sandbox.running.util import run_task
from utils.sandbox.util import Task

class TestTaskRunning:
    def test_with_test_task_should_change_the_task_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.status == StatusType.RUNNING

    @freeze_time("2002-06-25 00:00:00")
    def test_with_test_task_should_have_running_timestamp(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.flow["running"] == "2002-06-25 00:00:00"

    def test_compile_with_test_task_should_return_result(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            test_task.execute_type = ExecuteType.COMPILE.value
            initialize_task(test_task, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "exitcode" in test_task.result
            assert int(test_task.result["exitcode"]) == 0

    def test_execute_with_test_task_should_return_result(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            test_task.execute_type = ExecuteType.EXECUTE.value
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert int(test_task.result["compile"]["exitcode"]) == 0
            assert int(test_task.result["report"][0]["exitcode"]) == 0

    def test_judge_with_test_task_should_return_result(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert int(test_task.result["compile_detail"]["submit"]["exitcode"]) == 0
            assert int(test_task.result["compile_detail"]["solution"]["exitcode"]) == 0
            assert int(test_task.result["compile_detail"]["checker"]["exitcode"]) == 0
            assert test_task.result["judge_detail"][0]["verdict"] == "AC"
            assert test_task.result["judge_detail"][1]["verdict"] == "AC"

    def test_with_invalid_execute_type_should_return_error_result(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            test_task.execute_type = "Invalid_type"
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["error"] == "Invalid execute type."

class TestStatus:
    # Handle AC status
    def test_with_valid_codes_should_return_ac_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            print(json.dumps(test_task.result))
            
            assert "status" in test_task.result
            assert test_task.result["status"] == "AC"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "AC"
            assert "ok" in last_judge_detail["log"]

    def test_with_valid_codes_should_return_message_ok(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "message" in test_task.result
            assert test_task.result["message"] == "OK."

    def test_with_valid_codes_should_return_correct_compile_detail_info(self, app: Flask, cleanup_test_sandbox: None, test_task: Task):
        with app.app_context():
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "compile_detail" in test_task.result
            assert "solution" in test_task.result["compile_detail"]
            assert "submit" in test_task.result["compile_detail"]
            assert "checker" in test_task.result["compile_detail"]
            assert test_task.result["compile_detail"]["solution"]["exitcode"] == "0"
            assert test_task.result["compile_detail"]["submit"]["exitcode"] == "0"
            assert test_task.result["compile_detail"]["checker"]["exitcode"] == "0"
        
    # Handle SCE status
    def test_with_invalid_solution_should_return_sce_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, wrong_syntax_code: str):
        with app.app_context():
            test_task.solution_code.code = wrong_syntax_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "status" in test_task.result
            assert "message" in test_task.result
            assert test_task.result["status"] == "SCE"
            assert test_task.result["message"] == "Solution compile failed."
        
    def test_with_invalid_solution_should_return_correct_compile_detail_info(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, wrong_syntax_code: str):
        with app.app_context():
            test_task.solution_code.code = wrong_syntax_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "compile_detail" in test_task.result
            assert "judge_detail" not in test_task.result
            assert "solution" in test_task.result["compile_detail"]
            assert "submit" not in test_task.result["compile_detail"]
            assert "checker" not in test_task.result["compile_detail"]
            assert test_task.result["compile_detail"]["solution"]["exitcode"] == "1"

    # Handle CCE status
    def test_with_invalid_checker_should_return_cce_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, wrong_syntax_code: str):
        with app.app_context():
            test_task.checker_code.code = wrong_syntax_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "status" in test_task.result
            assert "message" in test_task.result
            assert test_task.result["status"] == "CCE"
            assert test_task.result["message"] == "Checker compile failed."

    def test_with_invalid_checker_should_return_correct_compile_detail_info(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, wrong_syntax_code: str):
        with app.app_context():
            test_task.checker_code.code = wrong_syntax_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "compile_detail" in test_task.result
            assert "judge_detail" not in test_task.result
            assert "solution" in test_task.result["compile_detail"]
            assert "checker" in test_task.result["compile_detail"]
            assert "submit" not in test_task.result["compile_detail"]
            assert test_task.result["compile_detail"]["solution"]["exitcode"] == "0"
            assert test_task.result["compile_detail"]["checker"]["exitcode"] == "1"

    # Handle CE status
    def test_with_invalid_user_code_should_return_ce_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, wrong_syntax_code: str):
        with app.app_context():
            test_task.user_code.code = wrong_syntax_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "status" in test_task.result
            assert "message" in test_task.result
            assert test_task.result["status"] == "CE"
            assert test_task.result["message"] == "Submit code compile failed."

    def test_with_invalid_user_code_should_return_correct_compile_detail_info(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, wrong_syntax_code: str):
        with app.app_context():
            test_task.user_code.code = wrong_syntax_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "compile_detail" in test_task.result
            assert "judge_detail" not in test_task.result
            assert "solution" in test_task.result["compile_detail"]
            assert "checker" in test_task.result["compile_detail"]
            assert "submit" in test_task.result["compile_detail"]
            assert test_task.result["compile_detail"]["solution"]["exitcode"] == "0"
            assert test_task.result["compile_detail"]["checker"]["exitcode"] == "0"
            assert test_task.result["compile_detail"]["submit"]["exitcode"] == "1"

    # Handle SRE status
    def test_with_solution_runtime_error_should_return_sre_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, runtime_error_code: str):
        with app.app_context():
            test_task.solution_code.code = runtime_error_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "SRE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "SRE"
            assert last_judge_detail["log"] == "The programming return exitsig 8" # Since runtime error code will trigger divided-by-zero, the exitcode will be 8.

    # Handle STLE status
    def test_with_solution_time_limit_exceeded_should_return_stle_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, timeout_code: str):
        with app.app_context():
            test_task.solution_code.code = timeout_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "STLE"
            assert "The programming has reached the time limit." in last_judge_detail["log"]
        
    # Handle RE status
    def test_with_user_code_runtime_error_should_return_re_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, runtime_error_code: str):
        with app.app_context():
            test_task.user_code.code = runtime_error_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "RE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "RE"
            assert last_judge_detail["log"] == "The programming return exitsig 8" # Since runtime error code will trigger divided-by-zero, the exitcode will be 8.

    # Handle TLE status
    def test_with_user_code_time_limit_exceeded_should_return_tle_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, timeout_code: str):
        with app.app_context():
            test_task.user_code.code = timeout_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "TLE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "TLE"
            assert "The programming has reached the time limit." in last_judge_detail["log"]

    # Handle WA status
    def test_with_user_code_wrong_answer_should_return_wa_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, wrong_answer_code: str):
        with app.app_context():
            test_task.user_code.code = wrong_answer_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "WA"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "WA"
            assert "wrong answer" in last_judge_detail["log"]

    #Handle CTLE status
    def test_with_checker_code_time_limit_exceeded_should_return_ctle_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, checker_timed_out_code: str):
        with app.app_context():
            test_task.checker_code.code = checker_timed_out_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "CTLE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "CTLE"
            assert "The programming has reached the time limit." in last_judge_detail["log"]

    #Handle CRE status
    def test_with_checker_code_runtime_error_should_return_cre_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, checker_runtime_error_code: str):
        with app.app_context():
            test_task.checker_code.code = checker_runtime_error_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "CRE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "CRE"
            assert "The programming return exitsig" in last_judge_detail["log"]

    #Handle SMLE status
    def test_with_solution_memory_limit_exceeded_code_should_return_smle_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, memoryout_code: str):
        with app.app_context():
            test_task.solution_code.code = memoryout_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "SMLE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "SMLE"
            assert "The programming has reached the memory limit." in last_judge_detail["log"]
    
    #Handle MLE status
    def test_with_user_code_memory_limit_exceeded_code_should_return_mle_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, memoryout_code: str):
        with app.app_context():
            test_task.user_code.code = memoryout_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "MLE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "MLE"
            assert "The programming has reached the memory limit." in last_judge_detail["log"]
    
    #Handle CMLE status
    def test_with_checker_code_memory_limit_exceeded_code_should_return_cmle_status(self, app: Flask, cleanup_test_sandbox: None, test_task: Task, checker_memory_out_code: str):
        with app.app_context():
            test_task.checker_code.code = checker_memory_out_code
            initialize_task(test_task, 0)
            initialize_test_case_to_sandbox(test_task, test_task.test_case, 0)
            
            run_task(test_task, test_task.test_case, 0)
            
            assert test_task.result["status"] == "CMLE"
            assert "judge_detail" in test_task.result
            last_judge_detail = test_task.result["judge_detail"][-1]
            assert last_judge_detail["verdict"] == "CMLE"
            assert "The programming has reached the memory limit." in last_judge_detail["log"]
