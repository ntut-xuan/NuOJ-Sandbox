from typing import Any

from utils.isolate.util import read_output, read_checker_log
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


def _judge_code(task: Task, box_id: int):
    result: dict[str, Any] = {
        "status": "",
        "message": "",
        "compile_detail": {}
    }

    compiled_solution_meta = compile_code(CodeType.SOLUTION, task.solution_code.compiler, box_id)
    result["compile_detail"]["solution"] = _fetch_compile_info_from_meta_file(compiled_solution_meta)
    if not _is_compiled_success(compiled_solution_meta):
        result["status"] = Verdict.SCE.value
        result["message"] = "Solution compile failed."
        return result

    compiled_checker_meta = compile_code(CodeType.CHECKER, task.checker_code.compiler, box_id)
    result["compile_detail"]["checker"] = _fetch_compile_info_from_meta_file(compiled_checker_meta)
    if not _is_compiled_success(compiled_checker_meta):
        result["status"] = Verdict.CCE.value
        result["message"] = "Checker compile failed."
        return result

    compiled_submit_meta = compile_code(CodeType.SUBMIT, task.user_code.compiler, box_id)
    result["compile_detail"]["submit"] = _fetch_compile_info_from_meta_file(compiled_submit_meta)
    if not _is_compiled_success(compiled_submit_meta):
        result["status"] = Verdict.CE.value
        result["message"] = "Submit code compile failed."
        return result

    result["judge_detail"]: list[dict[str, Any]] = []

    for i in range(len(task.test_case)):
        execute_result: dict[str, Any] = _execute_testcase(task, i, box_id)
        result["judge_detail"].append(execute_result)
        
        if(execute_result["verdict"] != Verdict.AC.value):
            result["status"] = execute_result["verdict"]
            result["message"] = execute_result["log"]
            return result

    result["status"] = Verdict.AC.value
    result["message"] = "OK."
    return result

def _execute_testcase(task: Task, testcase_index: int, box_id: int):
    execute_result = {
        "verdict": "",
        "output_set": {
            "submit": "",
            "answer": ""
        },
        "runtime_info": {},
        "log": ""
    }
    
    execute_solution_meta = execute_code(CodeType.SOLUTION, task.solution_code.compiler, task.options, testcase_index, box_id)
    execute_result["runtime_info"] |= {"solution": _fetch_execute_info_from_meta_file(execute_solution_meta)}
    
    if _handle_execute_exception(execute_solution_meta, execute_result, Verdict.SRE, Verdict.STLE, Verdict.SMLE):
        return execute_result

    execute_result["output_set"]["answer"] = read_output(testcase_index, CodeType.SOLUTION, box_id)

    execute_user_code_meta = execute_code(CodeType.SUBMIT, task.user_code.compiler, task.options, testcase_index, box_id)
    execute_result["runtime_info"] |= {"submit": _fetch_execute_info_from_meta_file(execute_user_code_meta)}
    
    if _handle_execute_exception(execute_user_code_meta, execute_result, Verdict.RE, Verdict.TLE, Verdict.MLE):
        return execute_result
    
    execute_result["output_set"]["submit"] = read_output(testcase_index, CodeType.SOLUTION, box_id)
    
    execute_checker_code_meta = judge_code(task, testcase_index, box_id)
    execute_result["runtime_info"] |= {"checker": _fetch_execute_info_from_meta_file(execute_checker_code_meta)}
    
    if _handle_execute_exception(execute_checker_code_meta, execute_result, Verdict.CRE, Verdict.CTLE, Verdict.CMLE):
        return execute_result
    
    if execute_checker_code_meta["exitcode"] == "0":
        execute_result["verdict"] = Verdict.AC.value    
        execute_result["log"] = read_checker_log(testcase_index, box_id)
    else:
        execute_result["verdict"] = Verdict.WA.value
        execute_result["log"] = read_checker_log(testcase_index, box_id)
    
    return execute_result
    

def _handle_execute_exception(meta: dict[str, Any], result: dict[str, Any], re_verdict: Verdict, tle_verdict: Verdict, mle_verdict: Verdict):
    # Handle MLE situation
    if "exitsig" in meta and meta["exitsig"] == "11":
        memory = meta["cg-mem"]
        result["verdict"] = mle_verdict.value
        result["log"] = f"The programming has reached the memory limit. ({memory}KB)"
        return True
    
    # Handle RE situation.
    if "exitsig" in meta:
        exitsig = meta["exitsig"]
        result["verdict"] = re_verdict.value
        result["log"] = f"The programming return exitsig {exitsig}"
        return True
    
    # Handle STLE situation
    if "status" in meta and meta["status"] == "TO":
        time = meta["time"]
        result["verdict"] = tle_verdict.value
        result["log"] = f"The programming has reached the time limit. ({time}s)"
        return True
    
    return False

def _fetch_compile_info_from_meta_file(meta: dict[str, Any]):
    return {"time": meta["time"], "memory": meta["cg-mem"], "exitcode": meta["exitcode"]}


def _fetch_execute_info_from_meta_file(meta: dict[str, Any]):
    execute_info: dict[str, Any] = {"time": meta["time"], "memory": meta["cg-mem"]}

    if "exitsig" in meta:
        execute_info |= {"exitsig": meta["exitsig"]}
    elif "exitcode" in meta:
        execute_info |= {"exitcode": meta["exitcode"]}

    return execute_info

def _is_compiled_success(meta: dict[str, Any]):
    return meta["exitcode"] == "0"
