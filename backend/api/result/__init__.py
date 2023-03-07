import json

from flask import Blueprint, Response


result_api_bp = Blueprint("result", __name__, url_prefix="/api/result")


@result_api_bp.route("/<uuid>/")
def result_return(uuid):
    """
    這是一個回傳的 route function，主要拿來獲取某個評測 uuid 的結果。
    """
    result = json.loads(
        open("/etc/nuoj-sandbox/storage/result/%s.result" % (uuid)).read()
    )
    return Response(json.dumps(result), mimetype="application/json")
