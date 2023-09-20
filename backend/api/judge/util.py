import json
import time
import threading
from typing import Any
from threading import Semaphore

import requests
from flask import current_app

from utils.isolate.util import cleanup_sandbox
from utils.sandbox.util import CodePackage, Task, TestCase, Option
from utils.sandbox.finish.util import finish_task
from utils.sandbox.inititalize.util import initialize_task, initialize_test_case_to_sandbox
from utils.sandbox.running.util import run_task
from storage.util import TunnelCode, write_file
    

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
            thread = FlaskThread(
                target=execute_task_with_specific_tracker_id,
                kwargs={"tracker_id": tracker_id},
            )
            thread.start()
        time.sleep(0.05)


def execute_task_with_specific_tracker_id(tracker_id):
    """
    這是主要處理測資評測的函數，首先會從檔案堆裡找出提交的 json file 與測資的 json file。
    接著會進行初始化、編譯、執行、評測、完成這五個動作，主要設計成盡量不要使用記憶體的空間，避免大量提交導致記憶體耗盡。
    """
    submission_data: dict[str, Any] = _fetch_json_object_from_storage(tracker_id)
    test_case: list[dict[str, Any]] = submission_data["test_case"]
    task = Task(
        checker_code=CodePackage(**submission_data["checker_code"]),
        solution_code=CodePackage(**submission_data["solution_code"]),
        user_code=CodePackage(**submission_data["user_code"]),
        execute_type=submission_data["execute_type"],
        test_case=[TestCase(**test_case[i]) for i in range(len(test_case))],
        test_case_size=0,
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
    initialize_test_case_to_sandbox(task, test_case, box_id)
    run_task(task, test_case, box_id)
    finish_task(task)

    # Store result to the storage
    _dump_task_result_to_storage(task, tracker_id)
    _send_webhook_with_webhook_url(task, tracker_id)

    # Free thread with release function.
    available_box.add(box_id)
    cleanup_sandbox(box_id)
    semaphores.release()
    return task.result


def _dump_task_result_to_storage(task: Task, tracker_id: int):
    result: dict[str, Any] = {
        "status": task.status.value,
        "flow": task.flow,
        "result": task.result
    }
    write_file(tracker_id + ".result", json.dumps(result), TunnelCode.RESULT)


def _fetch_json_object_from_storage(tracker_id: int) -> dict[str, Any]:
    raw_json_object: str
    storage_path: str = current_app.config["STORAGE_PATH"]
    with open(f"{storage_path}/submission/{tracker_id}.json") as f:
        raw_json_object = f.read()
    return json.loads(raw_json_object)


def _send_webhook_with_webhook_url(task: Task, tracker_id: int):
    if task.options.webhook_url is not None:
        resp = requests.post(
            task.options.webhook_url,
            data=json.dumps({"status": "OK", "data": task.result}),
            headers={"content-type": "application/json"},
            timeout=10
        )
        if resp.status_code != 200:
            print(f"webhook_url {task.options.webhook_url} has error that occur result {tracker_id} has error.")
        else:
            print(f"webhook_url {task.options.webhook_url} send successfully.")

class FlaskThread(threading.Thread):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.app: Flask = current_app._get_current_object()  # type: ignore[attr-defined]

    def run(self) -> None:
        with self.app.app_context():
            super().run()
