import json
from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, Response, current_app, make_response


result_api_bp = Blueprint("result", __name__, url_prefix="/api/result")


@result_api_bp.route("/<uuid>/")
def result_return(uuid):
    """
    這是一個回傳的 route function，主要拿來獲取某個評測 uuid 的結果。
    """
    storage_path: str = current_app.config["STORAGE_PATH"]
    result_path: Path = Path(f"{storage_path}/result/{uuid}.result")
    
    if not result_path.exists():
        return make_response({}, HTTPStatus.NOT_FOUND)
    
    with open(result_path) as file:
        result = json.loads(file.read())
        return Response(json.dumps(result), mimetype="application/json")
