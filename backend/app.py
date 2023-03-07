import json
import time
import threading
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any

from api.judge.route import judge_api_bp
from api.result.route import result_api_bp
from api.swagger.route import swagger_api_bp
from api.system.route import system_api_bp
from api.test_case.route import test_case_api_bp
from utils.sandbox_util import execute_queueing_task_when_exist_empty_box

from flask import Flask


def create_app(config_filename=None) -> Flask:
    app = Flask(__name__)
    app.register_blueprint(judge_api_bp)
    app.register_blueprint(result_api_bp)
    app.register_blueprint(swagger_api_bp)
    app.register_blueprint(system_api_bp)
    app.register_blueprint(test_case_api_bp)

    pop_work_timer = threading.Thread(target=execute_queueing_task_when_exist_empty_box)
    pop_work_timer.daemon = True
    pop_work_timer.start()

    return app
