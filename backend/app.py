import json
import time
import threading
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any
from threading import Semaphore

from api.judge.route import judge_api_bp
from api.judge.util import execute_queueing_task_when_exist_empty_box
from api.result.route import result_api_bp
from api.system.route import system_api_bp
from api.test.route import test_bp
from api.test_case.route import test_case_api_bp
from setting.util import Setting, SettingBuilder

from flask import Flask, current_app


def create_app(config_mapping: dict[str, str] = None) -> Flask:
    app = Flask(__name__)
    
    if config_mapping is not None:
        app.config.from_mapping(config_mapping)
    else:
        app.config.from_pyfile("config.py")
        
    setting: Setting = SettingBuilder().from_file("setting.json")
    app.config["avaliable_box"] = set([i for i in range(setting.sandbox_number)])
    app.config["setting"] = setting
    app.config["submission"] = []
    app.config["result_mapping"] = {}
    app.config["semaphores"] = Semaphore(setting.sandbox_number)
    
    app.register_blueprint(judge_api_bp)
    app.register_blueprint(result_api_bp)
    app.register_blueprint(system_api_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(test_case_api_bp)

    pop_work_timer = FlaskThread(app, target=execute_queueing_task_when_exist_empty_box)
    pop_work_timer.daemon = True
    pop_work_timer.start()

    return app


class FlaskThread(threading.Thread):
    def __init__(self, app, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.app: Flask = app  # type: ignore[attr-defined]

    def run(self) -> None:
        with self.app.app_context():
            super().run()
