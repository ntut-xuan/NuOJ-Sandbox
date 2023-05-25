from os import environ

import pytest

from tests.nocg.api.judge.test_route import TestSubmit, payload

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestSubmit(TestSubmit):
    pass