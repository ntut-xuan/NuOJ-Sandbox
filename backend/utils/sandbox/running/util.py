from typing import Any

from utils.isolate.util import read_output
from utils.sandbox.function.util import compile_code, execute_code, judge_code
from utils.sandbox.util import Task, TestCase, get_timestamp
from utils.sandbox.enum import CodeType, ExecuteType, StatusType, Verdict


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
        task.result = _judge_code(task, box_id)
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

def _judge_code(task: Task, box_id: int):
    result: dict[str, Any] = {
        "status": "",
        "message": "",
        "compile_detail": {}
    }

    compiled_solution_meta = compile_code(CodeType.SOLUTION, task.solution_code.compiler, box_id)
    result["compile_detail"]["solution"] = fetch_compile_info_from_meta_file(compiled_solution_meta)
    if not _is_compiled_success(compiled_solution_meta):
        result["status"] = Verdict.SCE.value
        result["message"] = "Solution compile failed."
        return result

    compiled_checker_meta = compile_code(CodeType.CHECKER, task.checker_code.compiler, box_id)
    result["compile_detail"]["checker"] = fetch_compile_info_from_meta_file(compiled_checker_meta)
    if not _is_compiled_success(compiled_checker_meta):
        result["status"] = Verdict.CCE.value
        result["message"] = "Checker compile failed."
        return result

    compiled_submit_meta = compile_code(CodeType.SUBMIT, task.user_code.compiler, box_id)
    result["compile_detail"]["submit"] = fetch_compile_info_from_meta_file(compiled_submit_meta)
    if not _is_compiled_success(compiled_submit_meta):
        result["status"] = Verdict.CE.value
        result["message"] = "Submit code compile failed."
        return result

    result["judge_detail"] = {}

    result["status"] = Verdict.OK.value
    result["message"] = "OK."
    return result

def fetch_compile_info_from_meta_file(meta: dict[str, Any]):
    return {"time": meta["time"], "memory": meta["cg-mem"], "exitcode": meta["exitcode"]}

def _is_compiled_success(meta: dict[str, Any]):
    return meta["exitcode"] == "0"
