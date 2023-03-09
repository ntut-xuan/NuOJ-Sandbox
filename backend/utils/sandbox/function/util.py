import traceback
from typing import Any

from utils.sandbox.enum import CodeType
from utils.sandbox.util import Task, TestCase, Option, meta_data_to_dict
from utils.isolate.util import compile, execute, checker

def compile_code(type: CodeType, compiler: str, box_id: int) -> dict[str, Any] | None:
    """
    這是一個編譯的函數，主要會將程式碼進行編譯，並回傳 meta dict。
    """
    try:
        meta: str = compile(type.value, compiler, box_id)
        meta_data = meta_data_to_dict(meta)
        meta_data["compile-status"] = "OK" if _is_compile_success(meta_data) else "Failed"
        return meta_data
    except Exception as e:
        print(traceback.format_exc())
        return None


def execute_code(type: CodeType, compiler: str, option: Option, testcase_index: int, box_id) -> dict[str, Any] | None:
    """
    這是一個執行的函數，運行指定的程式與測試資料，並回傳運行結果是否正常。
    """
    try:
        time = option.time
        wall_time = option.wall_time
        meta = execute(type.value, testcase_index, time, wall_time, compiler, box_id)
        meta_data = meta_data_to_dict(meta)
        return meta_data
    except Exception:
        print(traceback.format_exc())
        return None
    

def judge_code(task: Task, box_id) -> dict[str, Any] | None:
    """
    這是一個評測的函數，主要會編譯、執行並使用 checker 進行評測，回傳結果。
    """
    try:
        judge_report = []
        is_wa = False
        test_case: list[TestCase] = task.test_case
        
        for i in range(len(test_case)):
            judge_result: dict[str, Any] = _execute_checker_and_get_result(i, task.options, box_id)
            is_wa |= (judge_result["verdict"] != "AC")
            judge_report.append(judge_result)

        result: dict[str, Any] = {
            "report": judge_report,
            "verdict": "WA" if is_wa else "AC"
        }
        return result
    except Exception:
        print(traceback.format_exc())
        return None


def _is_compile_success(meta_data: dict[str, Any]) -> bool:
    return "status" not in meta_data


def _execute_checker_and_get_result(test_case_index: int, options: Option, box_id: int) -> dict[str, Any]:
    checker_meta = checker(test_case_index, options.time, options.wall_time, box_id)
    checker_meta_data = meta_data_to_dict(checker_meta)
    verdict: str = "AC" if checker_meta_data["exitcode"] == "0" else "WA"
    judge_result = {
        "verdict": verdict,
        "time": checker_meta_data["time"],
        "memory": checker_meta_data["cg-mem"]
    }
    return judge_result
