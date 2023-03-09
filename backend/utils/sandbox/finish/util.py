from utils.sandbox.enum import StatusType
from utils.sandbox.util import Task, get_timestamp

def finish_task(task: Task):
    task.status = StatusType.FINISH
    task.flow["finished"] = get_timestamp()
