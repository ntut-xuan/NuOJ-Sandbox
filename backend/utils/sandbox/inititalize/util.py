from utils.sandbox.util import Task, get_timestamp
from utils.sandbox.enum import CodeType, StatusType
from utils.isolate.util import init_sandbox, touch_text_file, touch_text_file_by_file_name


def initialize_task(task: Task, box_id: int) -> None:
    task.status = StatusType.INITIAL
    _initilize_sandbox(box_id)
    _initialize_code(task, box_id)


def _initilize_sandbox(box_id: int) -> None:
    """
    這是一個初始化的函數，會將沙盒初始化。
    """
    init_sandbox(box_id)


def _initialize_code(task: Task, box_id: int) -> None:
    """
    初始化任務的程式碼移置到沙盒的動作。
    """
    if task.user_code is not None:
        touch_text_file(
            task.user_code.code, CodeType.SUBMIT, task.user_code.compiler, box_id
        )
        task.flow["init_code"] = get_timestamp()

    if task.solution_code is not None:
        touch_text_file(
            task.solution_code.code, CodeType.SOLUTION, task.solution_code.compiler, box_id
        )
        task.flow["init_solution"] = get_timestamp()

    if task.checker_code is not None:
        touch_text_file(
            task.checker_code.code, CodeType.CHECKER, task.checker_code.compiler, box_id
        )
        task.flow["init_checker"] = get_timestamp()

    _initialize_testlib_to_sandbox(box_id)
    task.flow["touch_testlib"] = get_timestamp()


def _initialize_testlib_to_sandbox(box_id: int) -> None:
    with open("/etc/nuoj-sandbox/backend/testlib.h") as file:        
        touch_text_file_by_file_name(file.read(), "testlib.h", box_id)
