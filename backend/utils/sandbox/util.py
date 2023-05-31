from typing import Any
from datetime import datetime

from dataclasses import dataclass, field
from utils.sandbox.enum import ExecuteType, TestCaseType, StatusType


@dataclass
class TestCase:
    type: TestCaseType
    value: str

@dataclass
class CodePackage:
    code: str
    compiler: str

@dataclass
class Option:
    threading: bool
    time: float
    wall_time: float
    memory: int
    webhook_url: str | None = None

@dataclass
class Task:
    checker_code: CodePackage
    solution_code: CodePackage
    user_code: CodePackage
    execute_type: ExecuteType
    options: Option
    test_case: list[TestCase]
    flow: dict[str, Any] = field(default_factory=dict[str, Any])
    result: dict[str, Any] = field(default_factory=dict[str, Any])
    status: StatusType = StatusType.PENDING


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def meta_data_to_dict(meta):
    """
    將 meta text 轉成 meta dict。
    """
    meta_data = {}
    for data in meta.split("\n"):
        if ":" not in data:
            continue
        meta_data[data.split(":")[0]] = data.split(":")[1]
    return meta_data
