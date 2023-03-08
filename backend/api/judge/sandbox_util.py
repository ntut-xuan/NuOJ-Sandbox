import json
import time
import threading
import traceback
from dataclasses import dataclass, field
from typing import Any
from threading import Semaphore

import api.judge.isolate as isolate
from api.judge.sandbox_enum import (
    CodeType,
    ExecuteType,
    StatusType,
    TestCaseType,
    Language,
)

import requests
from dataclass_wizard import JSONWizard
from datetime import datetime
from flask import current_app


@dataclass
class TestCase(JSONWizard):
    type: TestCaseType
    value: str

@dataclass
class CodePackage:
    code: str
    compiler: Language

@dataclass
class Option:
    threading: bool
    time: float
    wall_time: float

@dataclass
class Task:
    checker_code: CodePackage
    solution_code: CodePackage
    user_code: CodePackage
    execute_type: ExecuteType
    options: Option
    test_case: list[TestCase]
    flow: dict[str, Any] = field(default_factory=dict[str, Any])
    result: dict[str, Any] = field(default_factory=dict[str, Any])
    status: StatusType = StatusType.PENDING




def execute_queueing_task_when_exist_empty_box():
    """
    這是一個執行序，會去找當前有沒有空的 box 可以做評測
    如果有的話，就會把提交丟到空的 box，沒有的話就會跳過，每一秒確認一次
    """
    while True:
        submission_list: list[str] = current_app.config["submission"]
        available_box: set[int] = current_app.config["avaliable_box"]
        if len(submission_list) > 0 and len(available_box) > 0:
            tracker_id = submission_list.pop(0)
            print(tracker_id)
            thread = threading.Thread(
                target=execute_task_with_specific_tracker_id,
                kwargs={"tracker_id": tracker_id},
            )
            thread.start()
        time.sleep(1)


def fetch_test_case_from_storage(filename: str) -> list[str]:
    json_object: list[str]
    storage_path: str = current_app.config["STORAGE_PATH"]
    with open(f"{storage_path}/testcase/{filename}.json", "r") as f:
        json_object = json.loads(f.read())
    return json_object


def initialize_task(task: Task, box_id: int) -> None:
    task.status = StatusType.INITIAL
    _initilize_sandbox(box_id)
    _initialize_code(task, box_id)


def _initilize_sandbox(box_id: int) -> None:
    """
    這是一個初始化的函數，會將沙盒初始化。
    """
    isolate.init_sandbox(box_id)


def _initialize_code(task: Task, box_id: int) -> None:
    """
    初始化任務的程式碼移置到沙盒的動作。
    """
    if task.user_code is not None:
        isolate.touch_text_file(
            task.user_code, CodeType.SUBMIT, task.user_code.compiler, box_id
        )
        task.flow["init_code"] = _get_timestamp()

    if task.solution_code is not None:
        isolate.touch_text_file(
            task.solution_code, CodeType.SOLUTION, task.solution_code.compiler, box_id
        )
        task.flow["init_solution"] = _get_timestamp()

    if task.checker_code is not None:
        isolate.touch_text_file(
            task.checker_code, CodeType.CHECKER, task.checker_code.compiler, box_id
        )
        task.flow["init_checker"] = _get_timestamp()

    _initialize_testlib_to_sandbox(box_id)
    task.flow["touch_testlib"] = _get_timestamp()


def _initialize_testlib_to_sandbox(box_id: int) -> None:
    isolate.touch_text_file_by_file_name(
        open("/etc/nuoj-sandbox/backend/testlib.h", "r").read(), "testlib.h", box_id
    )


def run_task(task: Task, test_case: list[str], box_id: int):
    task.status = StatusType.RUNNING
    task.flow["running"] = _get_timestamp()

    if task.execute_type == ExecuteType.COMPILE:
        task.result["result"] = compile(CodeType.SUBMIT, task.user_code.compiler, box_id)
    elif task.execute_type == ExecuteType.EXECUTE:
        result = {
            "compile": compile(CodeType.SUBMIT, task.user_code.compiler, box_id), 
            "report": []
        }
        report = []
        for i in range(len(task.test_case)):
            execute_meta_data = execute(CodeType.SUBMIT, task.user_code.compiler, task.options, i, box_id)
            report.append(execute_meta_data)
        result["report"] = report
        task.result["result"] = result
    elif task.execute_type == ExecuteType.JUDGE:
        result = {
            "compile": {
                "user_code": compile(CodeType.SUBMIT, task.user_code.compiler, box_id), 
                "solution_code": compile(CodeType.SOLUTION, task.user_code.compiler, box_id), 
                "checker_code": compile(CodeType.CHECKER, task.user_code.compiler, box_id)
            }, 
            "judge": {}
        }
        test_case: list[TestCase] = task.test_case
        for i in range(len(test_case)):
            execute(CodeType.SOLUTION, task.solution_code.compiler, task.options, i, box_id)
            execute(CodeType.SUBMIT, task.solution_code.compiler, task.options, i, box_id)
        result["judge"] = run_judge(task, box_id)
        task.result["result"] = result


def _get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def finish_task(task: Task):
    task.status = StatusType.FINISH
    task.flow["finished"] = _get_timestamp()


def dump_task_result_to_storage(task: Task, tracker_id: int):
    storage_path: str = current_app.config["STORAGE_PATH"]
    path = f"{storage_path}/result/{tracker_id}.result"

    with open(path, "w") as f:
        f.write(json.dumps(task.result, indent=4))


def fetch_json_object_from_storage(tracker_id: int) -> dict[str, Any]:
    raw_json_object: str
    storage_path: str = current_app.config["STORAGE_PATH"]
    with open(f"{storage_path}/submission/{tracker_id}.json") as f:
        raw_json_object = f.read()
    return json.loads(raw_json_object)


def send_webhook_with_webhook_url(task: Task, tracker_id: int):
    if "webhook_url" in task.options:
        resp = requests.post(
            task.options["webhook_url"],
            data=json.dumps({"status": "OK", "data": task.result}),
            headers={"content-type": "application/json"},
        )
        if resp.status_code != 200:
            print(
                "webhook_url "
                + task.options["webhook_url"]
                + " has error that occur result "
                + tracker_id
                + " has error."
            )
        else:
            json_data = json.loads(resp.text)
            if json_data["status"] != "OK":
                print(
                    "webhook_url "
                    + task.options["webhook_url"]
                    + " has error that occur result "
                    + tracker_id
                    + " send failed."
                )
            else:
                print(
                    "webhook_url " + task.options["webhook_url"] + " send successfully"
                )


def execute_task_with_specific_tracker_id(tracker_id):
    """
    這是主要處理測資評測的函數，首先會從檔案堆裡找出提交的 json file 與測資的 json file。
    接著會進行初始化、編譯、執行、評測、完成這五個動作，主要設計成盡量不要使用記憶體的空間，避免大量提交導致記憶體耗盡。
    """
    submission_data: dict[str, Any] = fetch_json_object_from_storage(tracker_id)
    task = Task(
        checker_code=CodePackage(**submission_data["checker_code"]),
        solution_code=CodePackage(**submission_data["solution_code"]),
        user_code=CodePackage(**submission_data["user_code"]),
        type=submission_data["type"],
        test_case=TestCase(**submission_data["test_case"]),
        options=Option(**submission_data["options"])
    )
    test_case: list[TestCase] = task.test_case

    available_box: set[int] = current_app.config["avaliable_box"]
    semaphores: Semaphore = current_app.config["semaphores"]

    # Bind thread with acquire
    semaphores.acquire()
    box_id = available_box.pop()

    # Execute the task
    initialize_task(task, box_id)
    initialize_test_case_to_sandbox(test_case, box_id)
    run_task(task, test_case, box_id)
    finish_task(task)

    # Store result to the storage
    dump_task_result_to_storage(task, tracker_id)
    send_webhook_with_webhook_url(task, tracker_id)

    # Free thread with release function.
    available_box.add(box_id)
    semaphores.release()
    finish(box_id)
    return task.result


def finish(box_id):
    """
    這是一個結束的函數，會將沙盒完全清除。
    """
    isolate.cleanup_sandbox(box_id)


def meta_data_to_dict(meta):
    """
    將 meta text 轉成 meta dict。
    """
    meta_data = {}
    for data in meta.split("\n"):
        if ":" not in data:
            continue
        meta_data[data.split(":")[0]] = data.split(":")[1]
    return meta_data


def initialize_test_case_from_storage_and_return_last_index(
    filename: str, start_index: int, box_id: int
) -> int:
    test_case_list: list[str] = fetch_test_case_from_storage(filename)
    for i in range(len(test_case_list)):
        isolate.touch_text_file_by_file_name(
            test_case_list[i], f"{i + start_index}.in", box_id
        )
    return start_index + len(test_case_list)


def initialize_test_case_from_plain_text_and_return_last_index(
    text: str, start_index: int, box_id: int
) -> int:
    isolate.touch_text_file_by_file_name(text, f"{start_index}.in", box_id)
    return start_index + 1


def initialize_test_case_to_sandbox(test_case_list: list[TestCase], box_id: int):
    index = 1
    for i in range(len(test_case_list)):
        test_case_object: TestCase = test_case_list[i]
        if test_case_object.use == TestCaseType.STATIC_FILE:
            index = initialize_test_case_from_storage_and_return_last_index(
                test_case_object.file, index, box_id
            )
        else:
            index = initialize_test_case_from_plain_text_and_return_last_index(
                test_case_object.text, index, box_id
            )


def compile(type: CodeType, language: Language, box_id: int) -> dict[str, Any] | None:
    """
    這是一個編譯的函數，主要會將程式碼進行編譯，並回傳 meta dict。
    """
    try:
        meta: str = isolate.compile(type.value, language, box_id)
        meta_data = meta_data_to_dict(meta)
        meta_data["compile-status"] = "OK" if _is_compile_success(meta_data) else "Failed"
        return meta_data
    except Exception as e:
        print(traceback.format_exc())
        return None


def execute(type: CodeType, language: Language, option: Option, testcase_index: int, box_id) -> dict[str, Any] | None:
    """
    這是一個執行的函數，運行指定的程式與測試資料，並回傳運行結果是否正常。
    """
    try:
        time = option.time
        wall_time = option.wall_time
        meta = isolate.execute(type.value, testcase_index, time, wall_time, language, box_id)
        meta_data = meta_data_to_dict(meta)
        return meta_data
    except Exception:
        print(traceback.format_exc())
        return None


def execute_checker_and_get_result(test_case_index: int, options: Option, box_id: int) -> dict[str, Any]:
    checker_meta = isolate.checker(test_case_index, options.time, options.wall_time, box_id)
    checker_meta_data = meta_data_to_dict(checker_meta)
    verdict: str = "AC" if checker_meta_data["exitcode"] == "0" else "WA",
    judge_result = {
        "verdict": verdict,
        "time": checker_meta_data["time"],
        "memory": checker_meta_data["cg-mem"]
    }
    return judge_result
    

def run_judge(task: Task, box_id) -> dict[str, Any] | None:
    """
    這是一個評測的函數，主要會編譯、執行並使用 checker 進行評測，回傳結果。
    """
    try:
        judge_report = []
        is_wa = False
        test_case: list[TestCase] = task.test_case
        
        for i in range(len(test_case)):
            judge_result: dict[str, Any] = execute_checker_and_get_result(i, task.options, box_id)
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


def _is_compile_success(meta_data: dict[str, Any]):
    return "status" in "meta_data"
