import json

from flask import Blueprint, Response, request
from storage.util import (
    TunnelCode,
    file_storage_tunnel_exist,
    file_storage_tunnel_read,
)

test_case_api_bp = Blueprint("test_case", __name__, url_prefix="/api/test_case")


@test_case_api_bp.route("/tc_upload", methods=["POST"])
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


@test_case_api_bp.route("/tc_fetch/<problem_pid>/", methods=["POST"])
def tc_fetch(problem_pid):
    """
    用於取得測資的部分，以及取得測資的數量
    """
    if file_storage_tunnel_exist(problem_pid + ".json", TunnelCode.TESTCASE) == False:
        return Response(
            json.dumps(
                {
                    "status": "Failed",
                    "message": "testcase " + problem_pid + " not exist",
                }
            ),
            mimetype="application/json",
        )

    testcase_raw = file_storage_tunnel_read(problem_pid + ".json", TunnelCode.TESTCASE)
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
