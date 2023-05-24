import warnings
from os import environ

import pytest

from tests.nocg.utils.sandbox.running.test_util import (
    TestStatus,
    TestTaskRunning,
)

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestTaskRunning(TestTaskRunning):
    pass

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestStatus(TestStatus):
    pass