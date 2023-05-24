from os import environ

import pytest

from tests.nocg.utils.sandbox.finish.test_util import (
    TestTaskFinish
)

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", False) == False, reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestTaskFinish(TestTaskFinish):
    pass