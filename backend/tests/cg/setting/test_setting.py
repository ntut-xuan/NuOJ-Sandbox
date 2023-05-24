from os import environ

import pytest

from tests.nocg.setting.test_setting import (
    setting,
    TestSetting
)

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", False) == False, reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestSetting(TestSetting):
    pass