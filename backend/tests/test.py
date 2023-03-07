from __future__ import annotations

import os
import sys
import json
import traceback

import pytest
import requests
from flask import Flask

# Check Sandbox heartbeat
"""
def service_heartbeat_test():
    try:
        response = test_client.get("/heartbeat")
        if response.status_code == 200:
            print("heartbeat test passed.")
        else:
            print("Failed at heartbeat test")
            sys.exit(1)
    except Exception as e:
        print(traceback.format_exc())
        print("Failed at heartbeat test")
        sys.exit(1)
"""


class TestJudge:
    def test_sandbox_with_cpp_submit(self, client: Flask):
        post_data = {
            "user_code": open("/etc/nuoj-sandbox/example_code/code.cpp", "r").read(),
            "solution_code": open(
                "/etc/nuoj-sandbox/example_code/solution.cpp", "r"
            ).read(),
            "checker_code": open(
                "/etc/nuoj-sandbox/example_code/checker.cpp", "r"
            ).read(),
            "test_case": [{"use": "plain-text", "text": "4 1 2 3 4"}],
            "execute_type": "J",
            "user_language": "cpp",
            "solution_language": "cpp",
            "checker_language": "cpp",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["result"]["report"]:
            assert data["verdict"] == "AC"

    def test_sandbox_with_py_submit(self, client: Flask):
        post_data = {
            "user_code": open("/etc/nuoj-sandbox/example_code/code.py", "r").read(),
            "solution_code": open(
                "/etc/nuoj-sandbox/example_code/solution.py", "r"
            ).read(),
            "checker_code": open(
                "/etc/nuoj-sandbox/example_code/checker.cpp", "r"
            ).read(),
            "test_case": [{"use": "plain-text", "text": "4 1"}],
            "execute_type": "J",
            "user_language": "py",
            "solution_language": "py",
            "checker_language": "cpp",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["result"]["report"]:
            assert data["verdict"] == "AC"

    def test_sandbox_with_golang_submit(self, client: Flask):
        post_data = {
            "user_code": open("/etc/nuoj-sandbox/example_code/code.go", "r").read(),
            "solution_code": open(
                "/etc/nuoj-sandbox/example_code/solution.go", "r"
            ).read(),
            "checker_code": open(
                "/etc/nuoj-sandbox/example_code/checker.cpp", "r"
            ).read(),
            "test_case": [{"use": "plain-text", "text": "8"}],
            "execute_type": "J",
            "user_language": "go",
            "solution_language": "go",
            "checker_language": "cpp",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["result"]["report"]:
            assert data["verdict"] == "AC"

    def test_sandbox_with_testcase_payload(self, client: Flask):
        post_data = {
            "user_code": open("/etc/nuoj-sandbox/example_code/code.cpp", "r").read(),
            "solution_code": open(
                "/etc/nuoj-sandbox/example_code/solution.cpp", "r"
            ).read(),
            "checker_code": open(
                "/etc/nuoj-sandbox/example_code/checker.cpp", "r"
            ).read(),
            "test_case": [{"use": "plain-text", "text": "4 2 5 7"}],
            "execute_type": "J",
            "user_language": "cpp",
            "solution_language": "cpp",
            "checker_language": "cpp",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["result"]["report"]:
            assert data["verdict"] == "AC"

    def test_sandbox_with_wrong_testcase_payload_should_return_400(self, client: Flask):
        post_data = {
            "user_code": open("/etc/nuoj-sandbox/example_code/code.cpp", "r").read(),
            "solution_code": open(
                "/etc/nuoj-sandbox/example_code/solution.cpp", "r"
            ).read(),
            "checker_code": open(
                "/etc/nuoj-sandbox/example_code/checker.cpp", "r"
            ).read(),
            "test_case": [{"use": "plain-text", "file": "testcase"}],
            "execute_type": "J",
            "user_language": "cpp",
            "solution_language": "cpp",
            "checker_language": "cpp",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))

        assert req.status_code == 400
