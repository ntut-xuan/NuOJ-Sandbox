import os
import sys
import requests
import json
import traceback
from sandbox_be import app

test_client = app.test_client()

# Check Sandbox heartbeat
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

# Check Sandbox working correctly.
def sandbox_test_for_cpp():
    try:
        post_data = {"user_code": open("/etc/nuoj-sandbox/example_code/code.cpp", "r").read(),
                    "solution_code": open("/etc/nuoj-sandbox/example_code/solution.cpp", "r").read(),
                    "checker_code": open("/etc/nuoj-sandbox/example_code/checker.cpp", "r").read(), 
                    "execute_type": "J", 
                    "user_language": "cpp", 
                    "solution_language": "cpp", 
                    "checker_language": "cpp",
                    "options": {"threading": False, "time": 4, "wall_time": 4}}
        
        req = test_client.post("/judge" ,data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["result"]["report"]:
            if data["verdict"] != "AC":
                print("verdict check: Error")
                sys.exit(1)

        print("sandbox test #1 passed.")
    except Exception as e:
        print(traceback.format_exc())
        print("Failed at sandbox test #1")
        sys.exit(1)

# Check Sandbox working correctly.
def sandbox_test_for_py():
    try:
        post_data = {
                    "user_code": open("/etc/nuoj-sandbox/example_code/code.py", "r").read(),
                    "solution_code": open("/etc/nuoj-sandbox/example_code/solution.py", "r").read(),
                    "checker_code": open("/etc/nuoj-sandbox/example_code/checker.cpp", "r").read(),
                    "execute_type": "J", 
                    "user_language": "py", 
                    "solution_language": "py", 
                    "checker_language": "cpp",
                    "options": {"threading": False, "time": 4, "wall_time": 4}}
        
        req = test_client.post("/judge" ,data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["result"]["report"]:
            if data["verdict"] != "AC":
                print("verdict check: Error")
                sys.exit(1)

        print("sandbox test #2 passed.")
    except Exception as e:
        print(traceback.format_exc())
        print("Failed at sandbox test #2 ")
        sys.exit(1)

# Check Sandbox working correctly.
def sandbox_test_for_c():
    try:
        post_data = {"user_code": open("/etc/nuoj-sandbox/example_code/code.c", "r").read(),
                    "solution_code": open("/etc/nuoj-sandbox/example_code/solution.c", "r").read(),
                    "checker_code": open("/etc/nuoj-sandbox/example_code/checker.cpp", "r").read(), 
                    "execute_type": "J", 
                    "user_language": "c", 
                    "solution_language": "c", 
                    "checker_language": "cpp",
                    "options": {"threading": False, "time": 4, "wall_time": 4}}
        
        req = test_client.post("/judge" ,data=json.dumps(post_data))
        response_data = json.loads(req.data)

        for data in response_data["result"]["result"]["report"]:
            if data["verdict"] != "AC":
                print("verdict check: Error")
                sys.exit(1)

        print("sandbox test #3 passed.")
    except Exception as e:
        print(traceback.format_exc())
        print("Failed at sandbox test #3")
        sys.exit(1)

service_heartbeat_test()
sandbox_test_for_cpp()
sandbox_test_for_py()
sandbox_test_for_c()
sys.exit(0)
