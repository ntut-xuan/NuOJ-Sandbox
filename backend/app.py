import json
import time
import threading
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any

from route.route import app_route
from route.swagger.route import swagger_bp
from utils.sandbox_util import execute_queueing_task_when_exist_empty_box

from flask import Flask

def create_app(config_filename = None) -> Flask:
    app = Flask(__name__)
    app.register_blueprint(app_route)
    app.register_blueprint(swagger_bp)
    
    pop_work_timer = threading.Thread(target=execute_queueing_task_when_exist_empty_box)
    pop_work_timer.daemon = True
    pop_work_timer.start()
    
    return app
