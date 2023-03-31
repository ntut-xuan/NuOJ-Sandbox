import traceback
from typing import Any

from utils.sandbox.enum import CodeType
from utils.sandbox.util import Task, TestCase, Option, meta_data_to_dict
from utils.isolate.util import compile, execute, checker, read_checker_log

def compile_code(type: CodeType, compiler: str, box_id: int) -> dict[str, Any] | None:
    """
    這是一個編譯的函數，主要會將程式碼進行編譯，並回傳 meta dict。
    """
    meta: str = compile(type.value, compiler, box_id)
    meta_data = meta_data_to_dict(meta)
    meta_data["compile-status"] = "OK" if _is_compile_success(meta_data) else "Failed"
    return meta_data


def execute_code(type: CodeType, compiler: str, option: Option, testcase_index: int, box_id) -> dict[str, Any] | None:
    """
    這是一個執行的函數，運行指定的程式與測試資料，並回傳運行結果是否正常。
    """
    time = option.time
    wall_time = option.wall_time
    meta = execute(type.value, testcase_index, time, wall_time, compiler, box_id)
    meta_data = meta_data_to_dict(meta)
    return meta_data
    

def judge_code(task: Task, testcase_index: int, box_id) -> dict[str, Any] | None:
    """
    這是一個評測的函數，主要會編譯、執行並使用 checker 進行評測，回傳結果。
    """
    options: Option = task.options
    meta = checker(testcase_index, options.time, options.wall_time, box_id)
    meta_data = meta_data_to_dict(meta)
    return meta_data


def _is_compile_success(meta_data: dict[str, Any]) -> bool:
    return "status" not in meta_data
