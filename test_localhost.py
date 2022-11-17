import os
import sys
import requests
import json
import traceback

# Check Sandbox working correctly.
def sandbox_test():
    try:
        post_data = {"code": open("./example_code/code.cpp", "r").read(),
                    "solution": open("./example_code/solution.cpp", "r").read(),
                    "checker": open("./example_code/checker.cpp", "r").read(), 
                    "execution": "J", 
                    "code_language": "cpp", 
                    "solution_language": "cpp", 
                    "checker_language": "cpp",
                    "option": {"threading": False, "time": 4, "wall_time": 4}}
        
        req = requests.post("http://localhost:4439/judge", data=json.dumps(post_data))
        response_data = json.loads(req.text)

        for data in response_data["result"]["result"]["report"]:
            if data["verdict"] != "AC":
                print("verdict check: Error")
                sys.exit(1)

        print("sandbox test passed.")
    except Exception as e:
        print(traceback.format_exc())
        print("Failed at sandbox test")
        sys.exit(1)

sandbox_test()
sys.exit(0)