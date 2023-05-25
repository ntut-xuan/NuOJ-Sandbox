import pytest
from freezegun import freeze_time

from utils.sandbox.enum import StatusType
from utils.sandbox.util import Task
from utils.sandbox.finish.util import finish_task

def test_with_test_task_should_change_the_task_status(cleanup_test_sandbox: None, test_task: Task):
    finish_task(test_task)
    
    assert test_task.status == StatusType.FINISH

@freeze_time("2002-06-25 00:00:00")
def test_with_test_task_should_have_running_timestamp(cleanup_test_sandbox: None, test_task: Task):
    finish_task(test_task)
    
    assert test_task.flow["finished"] == "2002-06-25 00:00:00"
