import os
import sys
import requests
import json
import traceback

# Check Service is OK.
def service_test():
    status = os.system('systemctl is-active --quiet nuoj-sandbox')
    print(status)

    if status != 0:
        print("service test failed.")
        sys.exit(1)

    print("service test passed.")

# Check Sandbox heartbeat
def service_heartbeat_test():
    try:
        link = "http://127.0.0.1:4439/heartbeat"
        req = requests.get(link)
        response_data = json.loads(req.text)
        if req.status_code == 200: 
            print("heartbeat test passed.")
        else:
            print("Failed at heartbeat test")
            sys.exit(1)
    except Exception as e:
        print(traceback.format_exc())
        print("Failed at heartbeat test")
        sys.exit(1)

# Check Sandbox working correctly.
def sandbox_test():
    try:
        link = "http://127.0.0.1:4439/judge"
        post_data = {"code": open("./example_code/code.cpp", "r").read(),
                    "solution": open("./example_code/solution.cpp", "r").read(),
                    "checker": open("./example_code/checker.cpp", "r").read(), "testcase": [], 
                    "execution": "J", "option": {"threading": False, "time": 4, "wall_time": 4}}
        
        req = requests.post(link, data=json.dumps(post_data))
        response_data = json.loads(req.text)

        for data in response_data["result"]["result"]["report"]:
            if data["verdict"] != "AC":
                print("verdict check: Error")
                sys.exit(1)

        print("sandbox test passed.")
        sys.exit(0)
    except Exception as e:
        print(traceback.format_exc())
        print("Failed at sandbox test")
        sys.exit(1)

service_test()
service_heartbeat_test()
sandbox_test()