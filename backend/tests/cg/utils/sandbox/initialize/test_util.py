import warnings
from os import environ

import pytest

from tests.nocg.utils.sandbox.initialize.test_util import (
    TestInitializeTask,
    TestInitializeTestCase
)
 
# Since "TestCase", "TestCaseType" is start with "Test", so it will be confirm a Test Class by Pytest and raise the warning.
# We need to filter the warning by warnings.filterwarnings.
warnings.filterwarnings("ignore", message="cannot collect test class .+")

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestInitializeTask(TestInitializeTask):
    pass

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestInitializeTestCase(TestInitializeTestCase):
    pass