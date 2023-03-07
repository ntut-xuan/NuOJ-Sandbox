import json
import time
import threading
import traceback
from dataclasses import dataclass, field
from typing import Any

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


setting = json.loads(open("./setting.json", "r").read())
n = int(setting["sandbox_number"])
sem = threading.Semaphore(n)
result_map = {}
available_box = set([(i + 1) for i in range(n)])
submission_list = []


@dataclass
class TestCase(JSONWizard):
    use: TestCaseType
    text: str = field(default_factory=str)
    file: str = field(default_factory=str)


@dataclass
class Task(JSONWizard):
    checker_code: str
    checker_language: Language
    execute_type: ExecuteType
    options: dict[str, Any]
    solution_code: str
    solution_language: Language
    test_case: list[TestCase]
    user_code: str
    user_language: Language
    flow: dict[str, Any] = field(default_factory=dict[str, Any])
    result: dict[str, Any] = field(default_factory=dict[str, Any])
    status: StatusType = StatusType.PENDING


def create_current_time_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def execute_queueing_task_when_exist_empty_box():
    """
    這是一個執行序，會去找當前有沒有空的 box 可以做評測
    如果有的話，就會把提交丟到空的 box，沒有的話就會跳過，每一秒確認一次
    """
    while True:
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


def initialize_testlib_to_sandbox(box_id: int) -> None:
    isolate.touch_text_file_by_file_name(
        open("/etc/nuoj-sandbox/backend/testlib.h", "r").read(), "testlib.h", box_id
    )


def initialize_code_for_prepare_sandbox(task: Task, box_id: int):
    """
    初始化任務的程式碼移置到沙盒的動作。
    """

    initilize_sandbox(box_id)

    if task.user_code is not None:
        isolate.touch_text_file(
            task.user_code, CodeType.SUBMIT, task.user_language, box_id
        )
        task.flow["init_code"] = create_current_time_string()

    if task.solution_code is not None:
        isolate.touch_text_file(
            task.solution_code, CodeType.SOLUTION, task.solution_language, box_id
        )
        task.flow["init_solution"] = create_current_time_string()

    if task.checker_code is not None:
        isolate.touch_text_file(
            task.checker_code, CodeType.CHECKER, task.checker_language, box_id
        )
        task.flow["init_checker"] = create_current_time_string()

    initialize_testlib_to_sandbox(box_id)
    task.flow["touch_testlib"] = create_current_time_string()


def initialize_task(task: Task, box_id: int):
    task.status = StatusType.INITIAL
    initialize_code_for_prepare_sandbox(task, box_id)


def run_task(task: Task, test_case: list[str], box_id: int):
    task.status = StatusType.RUNNING
    task.flow["running"] = create_current_time_string()

    language_map = {
        "submit_code": task.user_language,
        "solution": task.solution_language,
        "checker": task.checker_language,
    }
    time = task.options["time"]
    wall_time = task.options["wall_time"]

    if task.execute_type == ExecuteType.COMPILE:
        task.result["result"] = compile(language_map, CodeType.SUBMIT.value, box_id)
    elif task.execute_type == ExecuteType.EXECUTE:
        task.result["result"] = execute(
            language_map, CodeType.SUBMIT.value, time, wall_time, test_case, box_id
        )
    elif task.execute_type == ExecuteType.JUDGE:
        task.result["result"] = judge(language_map, test_case, time, wall_time, box_id)


def finish_task(task: Task):
    task.status = StatusType.FINISH
    task.flow["finished"] = create_current_time_string()


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
    data = fetch_json_object_from_storage(tracker_id)
    task = Task.from_dict(data)
    test_case: list[TestCase] = task.test_case

    # Bind thread with acquire
    sem.acquire()
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
    sem.release()
    finish(box_id)
    return task.result


def initilize_sandbox(box_id: int, option=None):
    """
    這是一個初始化的函數，會將沙盒初始化。
    """
    isolate.init_sandbox(box_id)


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


def compile(language_map, type, box_id, option=None):
    """
    這是一個編譯的函數，主要會將程式碼進行編譯，並回傳 meta dict。
    """
    try:
        meta = isolate.compile(type, language_map[type].value, box_id)
        meta_data = meta_data_to_dict(meta)

        if "status" in meta_data:
            meta_data["compile-result"] = "Failed"
        else:
            meta_data["compile-result"] = "OK"

        return meta_data
    except Exception as e:
        print(traceback.format_exc())
        return (str(traceback.format_exc()), False)


def execute(language_map, type, time, wall_time, testcase, box_id, option=None) -> dict:
    """
    這是一個執行的函數，主要會將測資放入沙盒，使用程式碼進行執行，並回傳結果。
    """
    try:
        output_data = []
        result_data = {}
        meta_data = compile(language_map, type, box_id)
        if meta_data["compile-result"] == "Failed":
            result_data["compile"] = meta_data
            return result_data
        output = isolate.execute(
            type, len(testcase), time, wall_time, language_map[type].value, box_id
        )
        for data in output:
            data_dict = {}
            data_dict["meta"] = meta_data_to_dict(data[0])
            data_dict["output"] = data[1]
            output_data.append(data_dict)
        result_data["compile"] = meta_data
        result_data["execute"] = output_data
        return result_data
    except Exception as e:
        print(traceback.format_exc())
        return (str(traceback.format_exc()), False)


def judge(language_map, testcase, time, wall_time, box_id, option=None):
    """
    這是一個評測的函數，主要會編譯、執行並使用 checker 進行評測，回傳結果。
    """
    try:
        result = {}
        # 編譯 checker
        result["checker-compile"] = compile(
            language_map, CodeType.CHECKER.value, box_id
        )
        if result["checker-compile"]["compile-result"] == "Failed":
            return result
        # 運行 solution
        result["solution_execute"] = execute(
            language_map, CodeType.SOLUTION.value, time, wall_time, testcase, box_id
        )
        if result["solution_execute"]["compile"]["compile-result"] == "Failed":
            return result
        # 運行 submit
        result["submit_execute"] = execute(
            language_map, CodeType.SUBMIT.value, time, wall_time, testcase, box_id
        )
        if result["submit_execute"]["compile"]["compile-result"] == "Failed":
            return result
        # 運行 judge
        judge_meta_list = isolate.checker(len(testcase), time, wall_time, box_id)
        judge_meta_data = []
        for data in judge_meta_list:
            judge_meta_data.append(meta_data_to_dict(data))
        result["judge_result"] = judge_meta_data

        report = []
        for i in range(len(judge_meta_data)):
            report_dict = {
                "verdict": "",
                "time": result["submit_execute"]["execute"][i]["meta"]["time"],
                "memory": result["submit_execute"]["execute"][i]["meta"]["cg-mem"],
            }
            report_dict["verdict"] = (
                "AC" if judge_meta_data[i]["exitcode"] == "0" else "WA"
            )
            report.append(report_dict)

        result["report"] = report

        verdict = "AC"
        for report_data in report:
            if report_data["verdict"] != "AC":
                verdict = report_data["verdict"]
                break

        result["verdict"] = verdict

        del result["judge_result"]
        del result["solution_execute"]["execute"]
        del result["submit_execute"]["execute"]

        return result
    except Exception as e:
        print(traceback.format_exc())
        return (str(traceback.format_exc()), False)
