import json
from http import HTTPStatus
from time import sleep
from typing import Any

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

@pytest.fixture
def payload(user_code: str, checker_code: str) -> dict[str, Any]:
    return {
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
            "memory": 131072,
            "time": 4,
            "wall_time": 4
        }
    }


def test_submit_code_with_no_threading_should_respond_http_status_code_ok(client: FlaskClient, payload: dict[str, Any]):
    response: TestResponse = client.post("/api/judge", json=payload)

    assert response.status_code == HTTPStatus.OK

def test_submit_code_with_threading_should_respond_http_status_code_ok(client: FlaskClient, payload: dict[str, Any]):
    payload["options"]["threading"] = True
    
    response: TestResponse = client.post("/api/judge", json=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    tracker_id = response.json["tracker_id"]
    _wait_status_finished(client, tracker_id)
    result_response: TestResponse= client.get(f"/api/result/{tracker_id}/")
    assert result_response.json["result"]["judge_detail"][0]["verdict"] == "AC"    


def _wait_status_finished(client: FlaskClient, tracker_id: str):
    attempt: int = 0
    while(attempt < 50):
        result_response: TestResponse= client.get(f"/api/result/{tracker_id}/")
        if result_response.status_code == 404:
            sleep(1)
            attempt += 1
            continue
        response_json: dict[str, Any] = result_response.json
        if response_json["status"] != "Finish":
            sleep(1)
            attempt += 1
            continue
        break
