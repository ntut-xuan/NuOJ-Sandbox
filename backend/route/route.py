import json
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

import utils.isolate as isolate
import utils.storage_util as storage_util
from utils.tunnel_code import TunnelCode
from utils.sandbox_util import available_box, submission_list, execute_task_with_specific_tracker_id

from dataclass_wizard import JSONWizard
from datetime import datetime
from flask import request, Response, Blueprint

app_route = Blueprint("app_route", __name__)

@app_route.route("/heartbeat", methods=["GET"])
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


@app_route.route("/result/<uuid>/", methods=["GET"])
def result_return(uuid):
    """
    這是一個回傳的 route function，主要拿來獲取某個評測 uuid 的結果。
    """
    result = json.loads(
        open("/etc/nuoj-sandbox/storage/result/%s.result" % (uuid)).read()
    )
    return Response(json.dumps(result), mimetype="application/json")


@app_route.route("/judge", methods=["POST"])
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


@app_route.route("/tc_upload", methods=["POST"])
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


@app_route.route("/tc_fetch/<problem_pid>/", methods=["POST"])
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
