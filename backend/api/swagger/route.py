import json
from typing import Any

from flask import Blueprint, make_response

swagger_api_bp = Blueprint("swagger", __name__)


@swagger_api_bp.route("/swagger_spec")
def fetch_swagger_spec_route():
    swagger_spec: str = None
    with open("./swagger/spec.json") as f:
        swagger_spec = f.read()
    swagger_spec_dict: dict[str, Any] = json.loads(swagger_spec)
    return make_response(swagger_spec_dict)


@swagger_api_bp.route("/api")
def api_page_route():
    with open("./swagger/page.html") as f:
        return f.read()
