#!/usr/bin/env python3
import isolate
import json
import time
import threading
import traceback
import uuid
from dataclasses import dataclass
from typing import Any

import storage_util
from dataclass_wizard import JSONWizard
from datetime import datetime
from sandbox_enum import CodeType, ExecuteType, Language, str2Language
from tunnel_code import TunnelCode

import requests
from flask import Flask, request, Response

setting = json.loads(open("/etc/nuoj-sandbox/setting.json", "r").read())
n = int(setting["sandbox_number"])
app = Flask(__name__)
sem = threading.Semaphore(n)
result_map = {}
available_box = set([(i + 1) for i in range(n)])
submission_list = []


@dataclass
class Task(JSONWizard):
    checker_code: str
    checker_language: Language
    execute_type: ExecuteType
    options: dict[str, Any]
    solution_code: str
    solution_language: Language
    user_code: str
    user_language: Language


def current_time_string() -> str:
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
            thread = threading.Thread(target=execute_task_with_specific_tracker_id, kwargs={"tracker_id": tracker_id})
            thread.start()
        time.sleep(1)


def fetch_test_case_from_storage() -> list[str]:
    json_object: list[str]
    with open("./testcase.json", "r") as f:
        json_object = json.loads(f.read())
    return json_object


def initial_testlib_to_sandbox(box_id: int) -> None:
    result = {"flow": {}}
    
    isolate.touch_text_file_by_file_name(open("/etc/nuoj-sandbox/testlib.h", "r").read(), "testlib.h", box_id)
    result["flow"]["touch_testlib"] = current_time_string()


def initial_code_for_prepare_sandbox(task: Task, box_id: int):
    result = {"flow": {}}

    init(task.user_code, task.user_language, CodeType.SUBMIT, box_id)
    result["flow"]["init_code"] = current_time_string()

    if task.solution_code is not None:
        init(task.solution_code, task.solution_language, CodeType.SOLUTION, box_id)
        result["flow"]["init_solution"] = current_time_string()

    if task.checker_code is not None:
        init(task.checker_code, task.checker_language, CodeType.CHECKER, box_id)
        result["flow"]["init_checker"] = current_time_string()
 
    initial_testlib_to_sandbox(box_id)


def execute_task_with_specific_tracker_id(tracker_id):
    """
    這是主要處理測資評測的函數，首先會從檔案堆裡找出提交的 json file 與測資的 json file。
    接著會進行初始化、編譯、執行、評測、完成這五個動作，主要設計成盡量不要使用記憶體的空間，避免大量提交導致記憶體耗盡。
    """
    data = json.loads(
        open("/etc/nuoj-sandbox/storage/submission/%s.json" % tracker_id, "r").read()
    )
    
    task = Task.from_dict(data)
    time = task.options["time"]
    wall_time = task.options["wall_time"]
    test_case = fetch_test_case_from_storage()
    result = {"flow": {}}

    sem.acquire()
    box_id = available_box.pop()

    result["status"] = "Initing"

    initial_code_for_prepare_sandbox(task, box_id)    

    result["status"] = "Running"
    result["flow"]["running"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    language_map = {
        "submit_code": task.user_language,
        "solution": task.solution_language,
        "checker": task.checker_language,
    }

    if task.execute_type == "C":
        result["result"] = compile(language_map, CodeType.SUBMIT.value, box_id)
    elif task.execute_type == "E":
        result["result"] = execute(
            language_map, CodeType.SUBMIT.value, time, wall_time, test_case, box_id
        )
    elif task.execute_type == "J":
        result["result"] = judge(language_map, test_case, time, wall_time, box_id)

    result["flow"]["finished"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result["status"] = "Finished"

    open("/etc/nuoj-sandbox/storage/result/%s.result" % tracker_id, "w").write(
        json.dumps(result)
    )

    if "webhook_url" in task.options:
        resp = requests.post(
            task.options["webhook_url"],
            data=json.dumps({"status": "OK", "data": result}),
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
                print("webhook_url " + task.options["webhook_url"] + " send successfully")

    available_box.add(box_id)
    sem.release()
    finish(box_id)
    return result


def init(code: str, language: Language, type: CodeType, box_id: int, option=None):
    """
    這是一個初始化的函數，會將沙盒初始化，並將程式碼放入沙盒。
    如果沙盒初始化了，那沙盒初始化這個動作就會被跳過。
    """
    isolate.init_sandbox(box_id)
    path, status = isolate.touch_text_file(code, type, language, box_id)
    return (path, status)


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
        for i in range(len(testcase)):
            isolate.touch_text_file_by_file_name(testcase[i], "%d.in" % (i + 1), box_id)
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


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    """
    這是一個心跳的 route function，主要會讓連接的機器確認是否活著，並且會回傳當前 judge server 的 core 與正在等待的評測數量。
    """
    result = {
        "status": "OK",
        "free_worker": len(available_box),
        "waiting_task": len(submission_list),
    }
    return Response(json.dumps(result), mimetype="application/json")


@app.route("/result/<uuid>/", methods=["GET"])
def result_return(uuid):
    """
    這是一個回傳的 route function，主要拿來獲取某個評測 uuid 的結果。
    """
    result = json.loads(
        open("/etc/nuoj-sandbox/storage/result/%s.result" % (uuid)).read()
    )
    return Response(json.dumps(result), mimetype="application/json")


@app.route("/judge", methods=["POST"])
def judge_route():
    """
    這是一個評測的 route function，主要讓使用者將資料 POST 到機器上，機器會將資料註冊成一個 uuid4 的 tracker_id。
    """
    data = json.loads(request.data.decode("utf-8"))
    execution_type = data["execute_type"]
    option = data["options"]
    status = None
    tracker_id = str(uuid.uuid4())

    open("/etc/nuoj-sandbox/storage/submission/%s.json" % tracker_id, "w").write(
        json.dumps(data)
    )
    del data

    if option["threading"]:
        submission_list.append(tracker_id)
    else:
        result = execute_task_with_specific_tracker_id(tracker_id)

    response = {"status": "OK", "type": execution_type, "tracker_id": tracker_id}
    if status == False:
        response["status"] = "Failed"

    if not option["threading"]:
        response["result"] = result

    return Response(json.dumps(response), mimetype="application/json")


@app.route("/tc_upload", methods=["POST"])
def tc_upload():
    """
    用於上傳測資的接口
    """
    data = request.json

    # fetch data
    problem_pid = data["problem_pid"]
    testcase_data = bytes(data["chunk"])

    # write file to back
    path = "/etc/nuoj-sandbox/storage/%s/%s" % (
        TunnelCode.TESTCASE.value,
        problem_pid + ".json",
    )
    with open(path, "ab") as file:
        file.write(testcase_data)

    return Response(json.dumps({"status": "OK"}), mimetype="application/json")


@app.route("/tc_fetch/<problem_pid>/", methods=["POST"])
def tc_fetch(problem_pid):
    """
    用於取得測資的部分，以及取得測資的數量
    """
    if (
        storage_util.file_storage_tunnel_exist(
            problem_pid + ".json", TunnelCode.TESTCASE
        )
        == False
    ):
        return Response(
            json.dumps(
                {
                    "status": "Failed",
                    "message": "testcase " + problem_pid + " not exist",
                }
            ),
            mimetype="application/json",
        )

    testcase_raw = storage_util.file_storage_tunnel_read(
        problem_pid + ".json", TunnelCode.TESTCASE
    )
    testcase_json_data = None

    try:
        testcase_json_data = json.loads(testcase_raw)
    except ValueError:
        return Response(
            json.dumps(
                {
                    "status": "Failed",
                    "message": "testcase " + problem_pid + " is broken",
                }
            ),
            mimetype="application/json",
        )

    data = {"status": "OK", "data": {"testcase_count": len(testcase_json_data)}}
    return Response(json.dumps(data), mimetype="application/json")


if __name__ == "__main__":
    pop_work_timer = threading.Thread(target=execute_queueing_task_when_exist_empty_box)
    pop_work_timer.daemon = True
    pop_work_timer.start()

    app.debug = True
    app.run(host="0.0.0.0", port=setting["port"], threaded=True)
