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


def replace_time_and_memory_attribute(payload: dict[str, Any]) -> dict[str, Any]:
    payload["tracker_id"] = "03e8a7f6-46b2-4195-9791-39f4f21cc96b"
    if "data" in payload:
        payload["data"]["compile_detail"]["solution"]["time"] = "0"
        payload["data"]["compile_detail"]["solution"]["memory"] = "0"
        payload["data"]["compile_detail"]["checker"]["time"] = "0"
        payload["data"]["compile_detail"]["checker"]["memory"] = "0"
        payload["data"]["compile_detail"]["submit"]["time"] = "0"
        payload["data"]["compile_detail"]["submit"]["memory"] = "0"

        for i in range(len(payload["data"]["judge_detail"])):
            payload["data"]["judge_detail"][i]["runtime_info"]["solution"]["time"] = "0"
            payload["data"]["judge_detail"][i]["runtime_info"]["solution"]["memory"] = "0"
            payload["data"]["judge_detail"][i]["runtime_info"]["submit"]["time"] = "0"
            payload["data"]["judge_detail"][i]["runtime_info"]["submit"]["memory"] = "0"
            payload["data"]["judge_detail"][i]["runtime_info"]["checker"]["time"] = "0"
            payload["data"]["judge_detail"][i]["runtime_info"]["checker"]["memory"] = "0"

    return payload


class TestSubmit:
    def test_submit_code_with_no_threading_should_respond_http_status_code_ok(self, client: FlaskClient, payload: dict[str, Any]):
        response: TestResponse = client.post("/api/judge", json=payload)

        assert response.status_code == HTTPStatus.OK

    def test_submit_code_with_no_threading_should_respond_correct_payload(self, client: FlaskClient, payload: dict[str, Any]):
        expected_payload: dict[str, Any] = {
            "status": "OK",
            "tracker_id": "03e8a7f6-46b2-4195-9791-39f4f21cc96b",
            "type": "Judge",
            "data": {
                "status": "AC",
                "message": "OK.",
                "compile_detail": {
                    "solution": {
                        "time": "1.188",
                        "memory": "156816",
                        "exitcode": "0"
                    },
                    "checker": {
                        "time": "1.717",
                        "memory": "158192",
                        "exitcode": "0"
                    },
                    "submit": {
                        "time": "1.012",
                        "memory": "156920",
                        "exitcode": "0"
                    }
                },
                "judge_detail": [
                    {
                        "verdict": "AC",
                        "output_set": {
                            "submit": "5",
                            "answer": "5"
                        },
                        "runtime_info": {
                            "solution": {
                                "time": "0.002",
                                "memory": "3656",
                                "exitcode": "0"
                            },
                            "submit": {
                                "time": "0.002",
                                "memory": "3560",
                                "exitcode": "0"
                            },
                            "checker": {
                                "time": "0.002",
                                "memory": "3884",
                                "exitcode": "0"
                            }
                        },
                        "log": "ok single line: '5'\n"
                    },
                    {
                        "verdict": "AC",
                        "output_set": {
                            "submit": "7",
                            "answer": "7"
                        },
                        "runtime_info": {
                            "solution": {
                                "time": "0.002",
                                "memory": "3628",
                                "exitcode": "0"
                            },
                            "submit": {
                                "time": "0.002",
                                "memory": "3656",
                                "exitcode": "0"
                            },
                            "checker": {
                                "time": "0.003",
                                "memory": "3832",
                                "exitcode": "0"
                            }
                        },
                        "log": "ok single line: '7'\n"
                    }
                ]
            }
        }
        response: TestResponse = client.post("/api/judge", json=payload)

        assert response.status_code == HTTPStatus.OK
        json: dict[str, Any] = response.get_json(silent=True)
        assert replace_time_and_memory_attribute(json) == replace_time_and_memory_attribute(expected_payload)

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
        assert response.json["data"]["judge_detail"][0]["verdict"] == "AC"  
        out, _ = capfd.readouterr()
        assert "send successfully" in out.split("\n")[-2]

    def test_submit_ce_status_report_with_webhooks_parameter_should_print_failed_message(self, client: FlaskClient, payload: dict[str, Any], capfd: Generator[pytest.CaptureFixture[str], None, None]):
        payload["options"]["webhook_url"] = "http://sandbox:4439/api/test/webhook"
        payload["user_code"]["code"] = ""
        
        response: TestResponse = client.post("/api/judge", json=payload)
        
        assert response.status_code == HTTPStatus.OK
        assert response.json["data"]["compile_detail"]["submit"]["exitcode"] == "1"  
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
