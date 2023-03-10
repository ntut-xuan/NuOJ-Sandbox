from typing import Any

from utils.isolate.util import read_output
from utils.sandbox.function.util import compile_code, execute_code, judge_code
from utils.sandbox.util import Task, TestCase, get_timestamp
from utils.sandbox.enum import CodeType, ExecuteType, StatusType


def run_task(task: Task, test_case: list[str], box_id: int):
    task.status = StatusType.RUNNING
    task.flow["running"] = get_timestamp()

    if task.execute_type == ExecuteType.COMPILE.value:
        task.result = compile_code(CodeType.SUBMIT, task.user_code.compiler, box_id)
    elif task.execute_type == ExecuteType.EXECUTE.value:
        result = {
            "compile": compile_code(CodeType.SUBMIT, task.user_code.compiler, box_id), 
            "report": []
        }
        report = []
        for i in range(len(task.test_case)):
            execute_meta_data = execute_code(CodeType.SUBMIT, task.user_code.compiler, task.options, i, box_id)
            report.append(execute_meta_data)
        result["report"] = report
        task.result = result
    elif task.execute_type == ExecuteType.JUDGE.value:
        result = {
            "compile": {
                "user_code": compile_code(CodeType.SUBMIT, task.user_code.compiler, box_id), 
                "solution_code": compile_code(CodeType.SOLUTION, task.solution_code.compiler, box_id), 
                "checker_code": compile_code(CodeType.CHECKER, task.checker_code.compiler, box_id)
            },
            "execute": [],
            "judge": {}
        }
        test_case: list[TestCase] = task.test_case
        for i in range(len(test_case)):
            execute_code(CodeType.SOLUTION, task.solution_code.compiler, task.options, i, box_id)
            execute_code(CodeType.SUBMIT, task.solution_code.compiler, task.options, i, box_id)
        result["execute"] = _fetch_all_of_input_and_user_output(task.test_case, box_id)
        result["judge"] = judge_code(task, box_id)
        task.result = result
    else:
        task.result = {"error": "Invalid execute type."}

def _fetch_all_of_input_and_user_output(test_case: list[TestCase], box_id: int) -> list[dict[str, Any]]:
    execute_results = []
    for i in range(len(test_case)):
        execute_results.append({
            "input": test_case[i].value,
            "output": read_output(i, CodeType.SUBMIT.value, box_id),
            "answer": read_output(i, CodeType.SOLUTION.value, box_id),
        })
    return execute_results
