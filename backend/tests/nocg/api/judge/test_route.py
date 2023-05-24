import json
from os import environ

from http import HTTPStatus
from time import sleep
from typing import Any, Generator

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

@pytest.fixture
def payload(user_code: str, checker_code: str) -> dict[str, Any]:
    return {
        "user_code": {
            "code": user_code,
            "compiler": "c++14"
        },
        "solution_code": {
            "code": user_code,
            "compiler": "c++14"
        },
        "checker_code": {
            "code": checker_code,
            "compiler": "c++14"
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

class TestSubmit:
    def test_submit_code_with_no_threading_should_respond_http_status_code_ok(self, client: FlaskClient, payload: dict[str, Any]):
        response: TestResponse = client.post("/api/judge", json=payload)

        assert response.status_code == HTTPStatus.OK

    def test_submit_code_with_threading_should_respond_http_status_code_ok(self, client: FlaskClient, payload: dict[str, Any]):
        payload["options"]["threading"] = True
        
        response: TestResponse = client.post("/api/judge", json=payload)

        assert response.status_code == HTTPStatus.OK
        assert response.json is not None
        tracker_id = response.json["tracker_id"]
        _wait_status_finished(client, tracker_id)
        result_response: TestResponse= client.get(f"/api/result/{tracker_id}/")
        assert result_response.json["result"]["judge_detail"][0]["verdict"] == "AC"    

    def test_submit_ok_status_report_with_webhooks_parameter_should_print_successfully_message(self, client: FlaskClient, payload: dict[str, Any], capfd: Generator[pytest.CaptureFixture[str], None, None]):
        payload["options"]["webhook_url"] = "http://sandbox:4439/api/test/webhook"
        
        response: TestResponse = client.post("/api/judge", json=payload)
        
        assert response.status_code == HTTPStatus.OK
        assert response.json["result"]["judge_detail"][0]["verdict"] == "AC"  
        out, _ = capfd.readouterr()
        assert "send successfully" in out.split("\n")[-2]

    def test_submit_ce_status_report_with_webhooks_parameter_should_print_failed_message(self, client: FlaskClient, payload: dict[str, Any], capfd: Generator[pytest.CaptureFixture[str], None, None]):
        payload["options"]["webhook_url"] = "http://sandbox:4439/api/test/webhook"
        payload["user_code"]["code"] = ""
        
        response: TestResponse = client.post("/api/judge", json=payload)
        
        assert response.status_code == HTTPStatus.OK
        assert response.json["result"]["compile_detail"]["submit"]["exitcode"] == "1"  
        out, _ = capfd.readouterr()
        assert "has error that occur result" in out.split("\n")[-2]


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