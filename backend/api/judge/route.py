import json
import uuid

from flask import Blueprint, Response, request
from utils.sandbox_util import execute_task_with_specific_tracker_id, submission_list
from utils.route_util import check_test_case_field_should_have_correct_data

judge_api_bp = Blueprint("judge", __name__, url_prefix="/api/judge")


@judge_api_bp.route("", methods=["POST"])
def judge_route():
    """
    這是一個評測的 route function，主要讓使用者將資料 POST 到機器上，機器會將資料註冊成一個 uuid4 的 tracker_id。
    """
    data = json.loads(request.data.decode("utf-8"))
    execution_type = data["execute_type"]
    option = data["options"]
    status = None
    tracker_id = str(uuid.uuid4())

    if not check_test_case_field_should_have_correct_data(data["test_case"]):
        return Response(
            {"status": "Failed", "Message": "Wrong test case payload."},
            mimetype="application/json",
            status=400,
        )

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
