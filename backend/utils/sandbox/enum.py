from enum import Enum


class CodeType(Enum):
    SUBMIT = "submit_code"
    SOLUTION = "solution"
    VALIDATE = "validate"
    CHECKER = "checker"
    META = "meta"


class ExecuteType(Enum):
    COMPILE = "Compile"
    EXECUTE = "Execute"
    JUDGE = "Judge"


class StatusType(Enum):
    PENDING = "Pending"
    INITIAL = "Initial"
    RUNNING = "Running"
    FINISH = "Finish"


class TestCaseType(Enum):
    STATIC_FILE = "static-file"
    PLAIN_TEXT = "plain-text"

class Language(Enum):
    CPP = "cpp"
    PYTHON = "py"
    JAVA = "java"
    GO = "go"
    NONE = ""

class Verdict(Enum):
    OK = "OK"
    CCE = "CCE"
    SCE = "SCE"
    CE = "CE"
