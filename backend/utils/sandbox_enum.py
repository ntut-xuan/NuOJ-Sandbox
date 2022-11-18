from enum import Enum

class CodeType(Enum):
    SUBMIT = "submit_code"
    SOLUTION = "solution"
    VALIDATE = "validate"
    CHECKER = "checker"
    META = "meta"


class Language(Enum):
    CPP = "cpp"
    PYTHON = "py"
    JAVA = "java"
    NONE = ""


class ExecuteType(Enum):
    COMPILE = "C"
    EXECUTE = "E"
    JUDGE = "J"


class StatusType(Enum):
    PENDING = "Pending"
    INITIAL = "Initial"
    RUNNING = "Running"
    FINISH = "Finish"

class TestCaseType(Enum):
    STATIC_FILE = "static-file"
    PLAIN_TEXT = "plain-text"


def str2Language(str):
    if str == "cpp":
        return Language.CPP
    elif str == "py":
        return Language.PYTHON
    elif str == "java":
        return Language.JAVA
