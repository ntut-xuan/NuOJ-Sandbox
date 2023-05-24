from os import environ

import pytest

from tests.nocg.storage.test_util import (
    TestDeleteFile,
    TestIsFileExists,
    TestReadFile,
    TestWriteFile,
    create_test_file
)

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestIsFileExists(TestIsFileExists):
    pass

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestWriteFile(TestWriteFile):
    pass

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestReadFile(TestReadFile):
    pass

@pytest.mark.skipif(environ.get("NUOJ_SANDBOX_ENABLE_CG", "0") == "0", reason="No or not enable CG Environment Variable [NUOJ_SANDBOX_ENABLE_CG]")
class TestDeleteFile(TestDeleteFile):
    pass