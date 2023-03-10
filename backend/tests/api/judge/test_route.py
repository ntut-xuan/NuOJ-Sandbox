import json
from http import HTTPStatus
from time import sleep
from typing import Any

import pytest
import requests
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

def test_submit_code_with_no_threading_should_respond_http_status_code_ok(client: FlaskClient, user_code: str, checker_code: str):
    excepted_payload: dict[str, str] = {
        "user_code": {
            "code": user_code,
            "compiler": "cpp"
        },
        "solution_code": {
            "code": user_code,
            "compiler": "cpp"
        },
        "checker_code": {
            "code": checker_code,
            "compiler": "cpp"
        },
        "test_case": [
            {
                "type": "plain-text",
                "value": "5"
            },
            {
                "type": "plain-text",
                "value": "7"
            }
        ],
        "execute_type": "Judge",
        "options": {
            "threading": False,
            "time": 4,
            "wall_time": 4
        }
    }
    
    response: TestResponse = client.post("/api/judge", json=excepted_payload)

    assert response.status_code == HTTPStatus.OK

def test_submit_code_with_threading_should_respond_http_status_code_ok(client: FlaskClient, user_code: str, checker_code: str):
    excepted_payload: dict[str, str] = {
        "user_code": {
            "code": user_code,
            "compiler": "cpp"
        },
        "solution_code": {
            "code": user_code,
            "compiler": "cpp"
        },
        "checker_code": {
            "code": checker_code,
            "compiler": "cpp"
        },
        "test_case": [
            {
                "type": "plain-text",
                "value": "5"
            },
            {
                "type": "plain-text",
                "value": "7"
            }
        ],
        "execute_type": "Judge",
        "options": {
            "threading": True,
            "time": 4,
            "wall_time": 4
        }
    }
    
    response: TestResponse = client.post("/api/judge", json=excepted_payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    tracker_id = response.json["tracker_id"]
    
    wait_status_finished(client, tracker_id)
    result_response: TestResponse= client.get(f"/api/result/{tracker_id}/")
    assert result_response.json["judge"]["verdict"] == "AC"    

def wait_status_finished(client: FlaskClient, tracker_id: str):
    while(True):
        result_response: TestResponse= client.get(f"/api/result/{tracker_id}/")
        if result_response.status_code == 404:
            sleep(1)
            continue
        response_json: dict[str, Any] = result_response.json
        if "judge" not in response_json:
            sleep(1)
            continue
        break
