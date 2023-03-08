from __future__ import annotations

import json

from flask import Flask

def fetch_code_with_specific_extension(filename: str, extension: str):
    with open(f"/etc/nuoj-sandbox/example_code/{filename}.{extension}") as f:
        return f.read()

class TestJudge:
    def test_sandbox_with_cpp_submit(self, client: Flask):
        post_data = {
            "user_code": {
                "code": fetch_code_with_specific_extension("code", "cpp"),
                "compiler": "cpp",
            },
            "solution_code": {
                "code": fetch_code_with_specific_extension("solution", "cpp"),
                "compiler": "cpp"
            },
            "checker_code": {
                "code": fetch_code_with_specific_extension("checker", "cpp"),
                "compiler": "cpp"
            },
            "test_case": [{"type": "plain-text", "value": "4 1 2 3 4"}, {"type": "plain-text", "value": "5 1 2 3 4 5"}],
            "execute_type": "Judge",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))        
        response_data = json.loads(req.data)

        for data in response_data["result"]["judge"]["report"]:
            assert data["verdict"] == "AC"

    def test_sandbox_with_py_submit(self, client: Flask):
        post_data = {
            "user_code": {
                "code": fetch_code_with_specific_extension("code", "py"),
                "compiler": "py",
            },
            "solution_code": {
                "code": fetch_code_with_specific_extension("solution", "py"),
                "compiler": "py"
            },
            "checker_code": {
                "code": fetch_code_with_specific_extension("checker", "cpp"),
                "compiler": "cpp"
            },
            "test_case": [{"type": "plain-text", "value": "5 11"}, {"type": "plain-text", "value": "6 2"}],
            "execute_type": "Judge",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["judge"]["report"]:
            assert data["verdict"] == "AC"

    def test_sandbox_with_golang_submit(self, client: Flask):
        post_data = {
            "user_code": {
                "code": fetch_code_with_specific_extension("code", "go"),
                "compiler": "go",
            },
            "solution_code": {
                "code": fetch_code_with_specific_extension("solution", "go"),
                "compiler": "go"
            },
            "checker_code": {
                "code": fetch_code_with_specific_extension("checker", "cpp"),
                "compiler": "cpp"
            },
            "test_case": [{"type": "plain-text", "value": "8"}],
            "execute_type": "Judge",
            "options": {"threading": False, "time": 4, "wall_time": 4},
        }

        req = client.post("/api/judge", data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["judge"]["report"]:
            assert data["verdict"] == "AC"
