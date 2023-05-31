import json

from flask import current_app

from loguru import logger
from setting.util import Setting
from storage.util import is_file_exists, TunnelCode
from storage.minio_util import download, is_testcase_in_storage_server
from utils.sandbox.util import Task, TestCase, get_timestamp
from utils.sandbox.enum import CodeType, StatusType, TestCaseType
from utils.isolate.util import init_sandbox, touch_text_file, touch_text_file_by_file_name


def initialize_task(task: Task, box_id: int) -> None:
    task.status = StatusType.INITIAL
    _initilize_sandbox(box_id)
    _initialize_code(task, box_id)


def initialize_test_case_to_sandbox(test_case_list: list[TestCase], box_id: int):
    index = 1
    for i in range(len(test_case_list)):
        test_case_object: TestCase = test_case_list[i]
        if test_case_object.type == TestCaseType.STATIC_FILE.value:
            index = _initialize_test_case_from_storage_and_return_last_index(test_case_object.value, index, box_id)
        else:
            index = _initialize_test_case_from_plain_text_and_return_last_index(test_case_object.value, index, box_id)


def _initilize_sandbox(box_id: int) -> None:
    """
    這是一個初始化的函數，會將沙盒初始化。
    """
    init_sandbox(box_id)


def _initialize_code(task: Task, box_id: int) -> None:
    """
    初始化任務的程式碼移置到沙盒的動作。
    """
    if task.user_code is not None:
        touch_text_file(
            task.user_code.code, CodeType.SUBMIT, task.user_code.compiler, box_id
        )
        task.flow["init_code"] = get_timestamp()

    if task.solution_code is not None:
        touch_text_file(
            task.solution_code.code, CodeType.SOLUTION, task.solution_code.compiler, box_id
        )
        task.flow["init_solution"] = get_timestamp()

    if task.checker_code is not None:
        touch_text_file(
            task.checker_code.code, CodeType.CHECKER, task.checker_code.compiler, box_id
        )
        task.flow["init_checker"] = get_timestamp()

    _initialize_testlib_to_sandbox(box_id)
    task.flow["touch_testlib"] = get_timestamp()


def _initialize_testlib_to_sandbox(box_id: int) -> None:
    with open("/etc/nuoj-sandbox/backend/testlib.h") as file:        
        touch_text_file_by_file_name(file.read(), "testlib.h", box_id)


def _initialize_test_case_from_storage_and_return_last_index(filename: str, start_index: int, box_id: int) -> int:
    assert _prepare_testcase_to_storage_directory(filename)
    test_case_list: list[str] = _fetch_test_case_from_storage(filename)
    for i in range(len(test_case_list)):
        touch_text_file_by_file_name(test_case_list[i], f"{i + start_index}.in", box_id)
    return start_index + len(test_case_list)


def _initialize_test_case_from_plain_text_and_return_last_index(text: str, start_index: int, box_id: int) -> int:
    touch_text_file_by_file_name(text, f"{start_index}.in", box_id)
    return start_index + 1


def _fetch_test_case_from_storage(filename: str) -> list[str]:
    json_object: list[str]
    storage_path: str = current_app.config["STORAGE_PATH"]
    with open(f"{storage_path}/testcase/{filename}.json", "r") as f:
        json_object = json.loads(f.read())
    return json_object


def _prepare_testcase_to_storage_directory(filename: str) -> bool:
    if is_file_exists(f"{filename}.json", TunnelCode.TESTCASE):
        return True
    
    setting: Setting = current_app.config["setting"]
    if setting.minio.enable and is_testcase_in_storage_server("testcase", filename):
        storage_path: str = current_app.config["STORAGE_PATH"]
        download("testcase", filename, f"{storage_path}/testcase/{filename}.json")
        return True
    
    return False