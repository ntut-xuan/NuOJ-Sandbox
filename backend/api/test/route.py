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
