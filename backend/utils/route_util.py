from typing import Any

from utils.sandbox_enum import TestCaseType


def check_test_case_field_should_have_correct_data(
    test_case_list: list[dict[str, Any]]
):
    for test_case_object in test_case_list:
        use: TestCaseType = TestCaseType(test_case_object["use"])
        if use == TestCaseType.PLAIN_TEXT and "text" not in test_case_object:
            return False
        if use == TestCaseType.STATIC_FILE and "file" not in test_case_object:
            return False
    return True
