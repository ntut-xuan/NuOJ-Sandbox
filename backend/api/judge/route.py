import json
import uuid

from flask import Blueprint, Response, current_app, request

from api.judge.util import execute_task_with_specific_tracker_id

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

    storage_path: str = current_app.config["STORAGE_PATH"]
    open(f"{storage_path}/submission/{tracker_id}.json", "w").write(
        json.dumps(data)
    )
    del data

    if option["threading"]:
        submission_list: list[str] = current_app.config["submission"]
        submission_list.append(tracker_id)
    else:
        result = execute_task_with_specific_tracker_id(tracker_id)

    response = {"status": "OK", "type": execution_type, "tracker_id": tracker_id}

    if not option["threading"]:
        response["data"] = result

    return Response(json.dumps(response), mimetype="application/json")
