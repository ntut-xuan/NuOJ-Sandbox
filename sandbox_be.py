#!/usr/bin/env python3
from flask import Flask, request, Response
from sandbox_enum import CodeType, Language
import isolate
import json
import threading
import traceback
import uuid
import time
from datetime import datetime

setting = json.loads(open("/opt/nuoj-sandbox/setting.json", "r").read())
n = int(setting["sandbox_number"])
app = Flask(__name__)
sem = threading.Semaphore(n)
result_map = {}
available_box = set([(i+1) for i in range(n)])
submission_list = []


def pop_work():
    '''
    這是一個執行序，會去找當前有沒有空的 box 可以做評測
    如果有的話，就會把提交丟到空的 box，沒有的話就會跳過，每一秒確認一次
    '''
    while True:
        if len(submission_list) > 0 and len(available_box) > 0:
            tracker_id =  submission_list.pop(0)
            print(tracker_id)
            thread = threading.Thread(target=do_work, kwargs={'tracker_id': tracker_id})
            thread.start()
        time.sleep(1)


def do_work(tracker_id):
    '''
    這是主要處理測資評測的函數，首先會從檔案堆裡找出提交的 json file 與測資的 json file。
    接著會進行初始化、編譯、執行、評測、完成這五個動作，主要設計成盡量不要使用記憶體的空間，避免大量提交導致記憶體耗盡。
    '''
    data = json.loads(open("/opt/nuoj-sandbox/submission/%s.json" % tracker_id, "r").read())
    option = data["option"]
    time = option["time"]
    wall_time = option["wall_time"]
    user_code = data["code"]
    test_case = json.loads(open("/opt/nuoj-sandbox/testcase.json", "r").read())
    execution_type = data["execution"]
    result = {}

    sem.acquire()
    box_id = available_box.pop()

    result[tracker_id] = {}
    result["flow"] = {}
    result["status"] = "Initing"

    _, status = init(user_code, Language.CPP.value, CodeType.SUBMIT.value, box_id)
    
    result["flow"]["init_code"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "solution" in data:
        solution_code = data["solution"]
        _, status = init(solution_code, Language.CPP.value, CodeType.SOLUTION.value, box_id)
        result["flow"]["init_solution"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "checker" in data:
        checker_code = data["checker"]
        _, status = init(checker_code, Language.CPP.value, CodeType.CHECKER.value, box_id)
        result["flow"]["init_checker"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    isolate.touch_text_file_by_file_name(open("/opt/nuoj-sandbox/testlib.h", "r").read(), "testlib.h", box_id)
    result["flow"]["touch_testlib"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result["status"] = "Running"
    result["flow"]["running"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if execution_type == "C":
        result["result"] = compile(Language.CPP.value, CodeType.SUBMIT.value, box_id)
    elif execution_type == "E":
        result["result"] = execute(Language.CPP.value, CodeType.SUBMIT.value, time, wall_time, test_case, box_id)
    elif execution_type == "J":
        result["result"] = judge(Language.CPP.value, test_case, time, wall_time, box_id)

    result["flow"]["finished"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result["status"] = "Finished"

    open("/opt/nuoj-sandbox/result/%s.result" % tracker_id, "w").write(json.dumps(result))

    available_box.add(box_id)
    sem.release()

    finish(box_id)
    return result


def init(code, language, type, box_id, option=None):
    '''
    這是一個初始化的函數，會將沙盒初始化，並將程式碼放入沙盒。
    如果沙盒初始化了，那沙盒初始化這個動作就會被跳過。
    '''
    isolate.init_sandbox(box_id)
    path, status = isolate.touch_text_file(code, type, language, box_id)
    return (path, status)


def finish(box_id):
    '''
    這是一個結束的函數，會將沙盒完全清除。
    '''
    isolate.cleanup_sandbox(box_id)


def meta_data_to_dict(meta):
    '''
    將 meta text 轉成 meta dict。
    '''
    meta_data = {}
    for data in meta.split("\n"):
        if(":" not in data):
            continue
        meta_data[data.split(":")[0]] = data.split(":")[1]
    return meta_data


def compile(language, type, box_id, option=None):
    '''
    這是一個編譯的函數，主要會將程式碼進行編譯，並回傳 meta dict。
    '''
    try:
        meta = isolate.compile(type, language, box_id)
        meta_data = meta_data_to_dict(meta)

        if "status" in meta_data:
            meta_data["compile-result"] = "Failed"
        else:
            meta_data["compile-result"] = "OK"       
        
        return meta_data
    except Exception as e:
        print(traceback.format_exc())
        return (str(traceback.format_exc()), False)


def execute(language, type, time, wall_time, testcase, box_id, option=None) -> dict:
    '''
    這是一個執行的函數，主要會將測資放入沙盒，使用程式碼進行執行，並回傳結果。
    '''
    try:
        output_data = []
        result_data = {}
        meta_data = compile(language, type, box_id)
        for i in range(len(testcase)):
            isolate.touch_text_file_by_file_name(testcase[i], "%d.in" % (i+1), box_id)
        if(meta_data["compile-result"] == "Failed"):
            result_data["compile"] = meta_data
            return result_data
        output = isolate.execute(type, len(testcase), time, wall_time, box_id)
        for data in output:
            data_dict = {}
            data_dict["meta"] = meta_data_to_dict(data[0])
            data_dict["output"] = data[1]
            output_data.append(data_dict)
        result_data["compile"] = meta_data
        result_data["execute"] = output_data
        return result_data
    except Exception as e:
        print(traceback.format_exc())
        return (str(traceback.format_exc()), False)


def judge(language, testcase, time, wall_time, box_id, option=None):
    '''
    這是一個評測的函數，主要會編譯、執行並使用 checker 進行評測，回傳結果。
    '''
    try:
        result = {}
        # 編譯 checker
        result["checker-compile"]  = compile(language, CodeType.CHECKER.value, box_id)
        if(result["checker-compile"]["compile-result"] == "Failed"):
            return result
        # 運行 solution
        result["solution_execute"] = execute(language, CodeType.SOLUTION.value, time, wall_time, testcase, box_id)
        if(result["solution_execute"]["compile"]["compile-result"] == "Failed"):
            return result
        # 運行 submit
        result["submit_execute"]   = execute(language, CodeType.SUBMIT.value, time, wall_time, testcase, box_id)
        if(result["submit_execute"]["compile"]["compile-result"] == "Failed"):
            return result
        # 運行 judge
        judge_meta_list = isolate.checker(len(testcase), time, wall_time, box_id)
        judge_meta_data = []
        for data in judge_meta_list:
            judge_meta_data.append(meta_data_to_dict(data))
        result["judge_result"] = judge_meta_data

        report = []
        for i in range(len(judge_meta_data)):
            report_dict = {"verdict": "", "time": result["submit_execute"]["execute"][i]["meta"]["time"]}
            report_dict["verdict"] =  "AC" if judge_meta_data[i]["exitcode"] == "0" else "WA"
            report.append(report_dict)

        result["report"] = report
        del result["judge_result"]
        del result["solution_execute"]["execute"]
        del result["submit_execute"]["execute"]

        return result
    except Exception as e:
        print(traceback.format_exc())
        return (str(traceback.format_exc()), False)


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    '''
    這是一個心跳的 route function，主要會讓連接的機器確認是否活著，並且會回傳當前 judge server 的 core 與正在等待的評測數量。
    '''
    result = {"status": "OK", "free_worker": len(available_box), "waiting_task": len(submission_list)}
    return Response(json.dumps(result), mimetype="application/json")


@app.route("/result/<uuid>/", methods=["GET"])
def result_return(uuid):
    '''
    這是一個回傳的 route function，主要拿來獲取某個評測 uuid 的結果。
    '''
    result = json.loads(open("/opt/nuoj-sandbox/result/%s.result" % (uuid)).read())
    return Response(json.dumps(result), mimetype="application/json")

@app.route("/judge", methods=["POST"])
def judge_route():
    '''
    這是一個評測的 route function，主要讓使用者將資料 POST 到機器上，機器會將資料註冊成一個 uuid4 的 tracker_id。
    '''
    data = json.loads(request.data.decode("utf-8"))
    execution_type = data["execution"]
    option = data["option"]
    status = None
    tracker_id = str(uuid.uuid4())

    open("/opt/nuoj-sandbox/submission/%s.json" % tracker_id, "w").write(json.dumps(data))
    del data

    if option["threading"]:
        submission_list.append(tracker_id)
    else:
        result = do_work(tracker_id)

    response = {"status": "OK", "type": execution_type, "tracker_id": tracker_id}
    if(status == False):
        response["status"] = "Failed"

    if not option["threading"]:
        response["result"] = result

    return Response(json.dumps(response), mimetype="application/json")


if __name__ == "__main__":
    pop_work_timer = threading.Thread(target=pop_work)
    pop_work_timer.daemon = True
    pop_work_timer.start()

    app.debug = True
    app.run(host="0.0.0.0", port=setting["port"], threaded=True)
