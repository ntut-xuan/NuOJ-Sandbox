import os
import sys
import requests
import json

# Check Service is OK.
status = os.system('systemctl is-active --quiet nuoj-sandbox')
print(status)


if status != 0:
    print("service test failed.")
    sys.exit(1)

print("service test passed.")

# Post Test
link = "http://localhost:3355/judge"
post_data = {"code": open("./example_code/code.cpp", "r").read(),
             "solution": open("./example_code/solution.cpp", "r").read(),
             "checker": open("./example_code/checker.cpp", "r").read(), "testcase": [], "execution": "J", "option": {"threading": False}}

for i in range(4):
    #print("read testdata %d" % (i+1))
    post_data["testcase"].append(open("./example_testcase/%d.in" % (i+1), "r").read())
req = requests.post(link, data=json.dumps(post_data))
response_data = json.loads(req.text)

for data in response_data["result"]["result"]["report"]:
    if data["verdict"] != "AC":
        print("verdict check: Error")
        sys.exit(1)

print("sandbox test passed.")
sys.exit(0)
