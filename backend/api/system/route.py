import json

from flask import Blueprint, Response, current_app

system_api_bp = Blueprint("system", __name__)


@system_api_bp.route("/heartbeat", methods=["GET"])
def heartbeat():
    """
    這是一個心跳的 route function，主要會讓連接的機器確認是否活著，並且會回傳當前 judge server 的 core 與正在等待的評測數量。
    """
    available_box: set[int] = current_app.config["avaliable_box"]
    submission_list: list[str] = current_app.config["submission_list"]
    
    result = {
        "status": "OK",
        "free_worker": len(available_box),
        "waiting_task": len(submission_list),
    }
    return Response(json.dumps(result), mimetype="application/json")
