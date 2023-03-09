from utils.sandbox.util import Task
from utils.sandbox.enum import CodeType, ExecuteType, StatusType

def run_task(task: Task, test_case: list[str], box_id: int):
    task.status = StatusType.RUNNING
    task.flow["running"] = _get_timestamp()

    if task.execute_type == ExecuteType.COMPILE.value:
        task.result = compile(CodeType.SUBMIT, task.user_code.compiler, box_id)
    elif task.execute_type == ExecuteType.EXECUTE.value:
        result = {
            "compile": compile(CodeType.SUBMIT, task.user_code.compiler, box_id), 
            "report": []
        }
        report = []
        for i in range(len(task.test_case)):
            execute_meta_data = execute(CodeType.SUBMIT, task.user_code.compiler, task.options, i, box_id)
            report.append(execute_meta_data)
        result["report"] = report
        task.result = result
    elif task.execute_type == ExecuteType.JUDGE.value:
        result = {
            "compile": {
                "user_code": compile(CodeType.SUBMIT, task.user_code.compiler, box_id), 
                "solution_code": compile(CodeType.SOLUTION, task.solution_code.compiler, box_id), 
                "checker_code": compile(CodeType.CHECKER, task.checker_code.compiler, box_id)
            }, 
            "judge": {}
        }
        test_case: list[TestCase] = task.test_case
        for i in range(len(test_case)):
            execute(CodeType.SOLUTION, task.solution_code.compiler, task.options, i, box_id)
            execute(CodeType.SUBMIT, task.solution_code.compiler, task.options, i, box_id)
        result["judge"] = run_judge(task, box_id)
        task.result = result
