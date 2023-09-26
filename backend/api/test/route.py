from http import HTTPStatus
from typing import Any

from flask import Blueprint, make_response, request

test_bp = Blueprint("test", __name__, url_prefix="/api/test")

# The test route for testing webhook when judge methods completed.
# Since it is just a test route, we assert json is not None and status filed exists.
# The status field will determine what status code should return. 
# When the verdict is AC it should return OK code and status OK in payload, otherwise, it should return status Forbidden code and failed message.
@test_bp.route("/webhook", methods=["POST"])
def test_webhooks():
    json: dict[str, Any] | None = request.get_json(silent=True)
    assert json is not None
    assert "status" in json
    
    if json["data"]["status"] == "AC":
        return make_response({"status": "OK"}, HTTPStatus.OK)
    else:
        return make_response({"message": "Failed"}, HTTPStatus.FORBIDDEN)

# The test route for testing debug webhook when judge is initialize
# We assume the payload should contains tracker_id and we confirm it by check the length of the tracker_id should be the same as GUID.
@test_bp.route("/debug_webhook", methods=["POST"])
def test_debug_webhooks():
    json: dict[str, Any] | None = request.get_json(silent=True)
    assert json is not None
    assert "tracker_id" in json
    
    if len(json["tracker_id"]) == len("e0dcbe84-3332-43b6-9060-54fb9e64a134"):
        return make_response({"status": "OK"}, HTTPStatus.OK)
    else:
        return make_response({"message": "Failed"}, HTTPStatus.FORBIDDEN)