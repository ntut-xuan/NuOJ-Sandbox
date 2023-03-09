# -*- coding: utf-8 -*-
"""
The Isolate toolbox by Uriah Xuan for developing NuOJ System.
Due to isolate is a command-execute program, so you can use this tool if you want :D
"""

import subprocess
import os
from utils.sandbox.enum import CodeType, Language


def generate_options_with_parameter(
    box_id: int | None = None,
    time: int | None = None,
    wall_time: int | None = None,
    extra_time: int | None = None,
    stack: int | None = None,
    open_files: int | None = None,
    fsize: int | None = None,
    stdin: str | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    meta: str | None = None,
    stderr_to_stdout: bool | None = False,
    max_processes: bool | None = False,
    share_net: bool = False,
    full_env: bool = False,
    cg: bool = False,
    cg_mem: int | None = None,
    cg_timing: int | None = None,
    dir: tuple[str, str] = None,
) -> str:
    values_options_map = {
        "--time": time,
        "--wall-time": wall_time,
        "--extra-time": extra_time,
        "--box-id": box_id,
        "--stack": stack,
        "--open-files": open_files,
        "--fsize": fsize,
        "--stdin": stdin,
        "--stdout": stdout,
        "--stderr": stderr,
        "--cg-mem": cg_mem,
        "--cg-timing": cg_timing,
        "--meta": meta,
    }
    boolean_options_map = {
        "--stderr-to-stdout": stderr_to_stdout,
        "--share-net": share_net,
        "--full-env": full_env,
        "--processes": max_processes,
        "--cg": cg,
    }

    options = ""

    for key in values_options_map.keys():
        if values_options_map[key] == None:
            continue
        options += f"{key}={values_options_map[key]} "

    for key in boolean_options_map.keys():
        if boolean_options_map[key] == False:
            continue
        options += f"{key} "

    if dir is not None:
        options += f"--dir={dir[0]}:{dir[1]} "

    return options


def generate_isolate_run_command(
    execute_command: str,
    box_id: int,
    wall_time: int | None = None,
    time: int | None = None,
    stdin: str | None = None,
    stdout: str | None = None,
    meta: str | None = None,
) -> str:
    # --box-id=%d --time=%d --wall-time=%d --cg-mem 256000 -p --full-env --meta='%s' --stdin='%d.in' --stdout='%s' --meta='%s'
    options = generate_options_with_parameter(
        box_id=box_id,
        time=time,
        wall_time=wall_time,
        full_env=True,
        stdin=stdin,
        stdout=stdout,
        max_processes=True,
        meta=meta,
        open_files=2048,
        cg=True,
        dir=("/root/.cache/go-build", "tmp"),
    )
    return f"isolate {options} --run -- {execute_command}"


def generate_isolate_init_command(box_id: int) -> str:
    options = generate_options_with_parameter(cg=True, box_id=box_id)
    return f"isolate {options} --init"


def generate_isolate_cleanup_command(box_id: int) -> str:
    options = generate_options_with_parameter(cg=True, box_id=box_id)
    return f"isolate {options} --cleanup"


def compile_command_generator(type, language: str):
    java_type = "Main" if type == CodeType.SUBMIT.value else "Solution"
    type = java_type if language == Language.JAVA.value else type
    compile_command_map = {
        Language.CPP.value: "/usr/bin/g++ %s.cpp -o %s.o" % (type, type),
        Language.JAVA.value: "/usr/bin/jdk-18.0.2.1/bin/javac %s.java" % type,
        Language.PYTHON.value: "/usr/bin/echo 'Python compile skiped.'",
        Language.GO.value: f"/usr/bin/go build -o {type}.o {type}.go",
    }
    return compile_command_map[language]


def execute_command(type, langauge: Language):
    java_type = "Main" if type == CodeType.SUBMIT.value else "Solution"
    execute_command_map = {
        Language.CPP.value: "%s.o" % type,
        Language.JAVA.value: "/usr/bin/jdk-18.0.2.1/bin/java %s" % java_type,
        Language.PYTHON.value: "/usr/bin/python3 %s.py" % type,
        Language.GO.value: f"{type}.o",
    }
    return execute_command_map[langauge]


def init_sandbox(box_id=0):
    """
    Initialize the specific ID of the sandbox.

        Args:
            box_id: The specific ID of the sandbox

    """
    command = generate_isolate_init_command(box_id)
    subprocess.call(command, shell=True)


def touch_text_file(text, type: CodeType, compiler: str, box_id=0) -> tuple:
    """
    Create a new text file and write text.

        Parameters:
            text: The text you want to write
            type: The type of code, reference CodeType class.
            langauge: The language of code, reference Langauge class.
            box_id: The ID of sandbox you want to create text file.

        Return:
            The Tuple object.
            The first element is the file's path that should create.
            The second element is the status, True for success, False otherwise.

    """
    java_type = "Main" if type == CodeType.SUBMIT else "Solution"
    type = java_type if compiler == Language.JAVA.value else type
    path = "/var/local/lib/isolate/%d/box/%s.%s" % (box_id, type.value, compiler)
    print("create file at", path)
    with open(path, "w") as code_file:
        code_file.write(text)
    if not os.path.exists(path):
        return (path, False)
    return (path, True)


def touch_text_file_by_file_name(text, filename, box_id=0) -> tuple:
    """
    Create a new text file with specific file name and write text.

        Parameters:
            text: The text you want to write
            filename: The name of file.
            box_id: The ID of sandbox you want to create text file.

        Return:
            The Tuple object.
            The first element is the file's path that should create.
            The second element is the status, True for success, False otherwise.
    """
    path = "/var/local/lib/isolate/%d/box/%s" % (box_id, filename)
    print("create file at", path)
    with open(path, "w") as code_file:
        code_file.write(text)
    if not os.path.exists(path):
        return (path, False)
    return (path, True)


def read_meta(box_id=0) -> str:
    """
    Return the meta file of text, the result after the Isolate run.

        Parameters:
            box_id: The ID of the sandbox you want to read the text of meta file.

        Return:
            A string, the text of meta file on the specific ID of the sandbox.

    """
    meta_path = "/var/local/lib/isolate/%d/box/meta.mt" % (box_id)
    with open(meta_path, "r") as code_file:
        return code_file.read()


def read_output(output_index, type, box_id=0) -> str:
    """
    Return the output file of text, the result after the Isolate run.

        Parameters:
            output_index: The index of the output file you want to read the text.
            box_id: The ID of the sandbox you want to read the text of meta file.

        Return:
            A string, the text of output file on the specific ID of the sandbox.

    """
    output_file = (
        "%d.out" % (output_index)
        if type == CodeType.SOLUTION.value
        else "%d.ans" % (output_index)
    )
    output_path = ("/var/local/lib/isolate/%d/box/" + output_file) % (box_id)
    with open(output_path, "r") as code_file:
        return code_file.read()


def cleanup_sandbox(box_id=0):
    """
    Cleanup the sandbox of the specific ID.

        Parameters:
            box_id: The ID of the sandbox you want to cleanup.

    """
    command = generate_isolate_cleanup_command(box_id)
    subprocess.call(command, shell=True)


def compile(type, language, box_id=0) -> str:
    """
    Compile the program on the specific ID of the sandbox.

        Parameters:
            type: The type of code, reference CodeType class.
            langauge: The language of code, reference Langauge class.
            box_id: The ID of the sandbox you want to compile the program.

        Return:
            A string of results on the meta file after finished compiled.

    """
    meta_path = "/var/local/lib/isolate/%d/box/meta.mt" % (box_id)
    compile_command = compile_command_generator(type, language)
    command = generate_isolate_run_command(
        compile_command, box_id, time=10, meta=meta_path
    )
    touch_text_file("init", CodeType.META, "mt", box_id)
    subprocess.call(command, shell=True)
    return read_meta(box_id)


def execute(type, test_case_index, time, wall_time, language, box_id=0) -> str:
    """
    Execute the program on the specific ID of the sandbox.

        Parameters:
            type: The type of code, reference CodeType class.
            test_case_count: The count of testcase.
            time: The time limit of program execute.
            wall_time: The wall time limit of program execute.
            language: The language of program.
            box_id: The ID of the sandbox you want to compile the program.

        Return:
            A string of results on the meta file after finished execute.

    """
    exec_command = execute_command(type, language)
    meta_path = "/var/local/lib/isolate/%d/box/meta.mt" % (box_id)
    touch_text_file("init", CodeType.META, "mt", box_id)
    input_file = f"{test_case_index+1}.in"
    output_file = (
        f"{test_case_index+1}.out"
        if type == CodeType.SOLUTION.value
        else f"{test_case_index+1}.ans"
    )
    command = generate_isolate_run_command(
        exec_command, box_id, wall_time, time, input_file, output_file, meta_path
    )
    touch_text_file_by_file_name("", output_file, box_id)
    print(f"Execute testcase {test_case_index+1}")
    subprocess.call(command, shell=True)
    meta = read_meta(box_id)
    return meta


def checker(test_case_index, time, wall_time, box_id):
    """
    Execute the checker program on the specific ID of the sandbox.

        Parameters:
            test_case_count: The count of testcase.
            box_id: The ID of the sandbox you want to compile the program.

        Return:
            A string of results on the meta file after finished check.

    """
    code_output = f"{CodeType.CHECKER.value}.o"
    meta_path = f"/var/local/lib/isolate/{box_id}/box/meta.mt"
    touch_text_file("init", CodeType.META, "mt", box_id)
    execute_command = f"{code_output} {test_case_index+1}.in {test_case_index+1}.out {test_case_index+1}.ans"
    command = generate_isolate_run_command(
        execute_command, box_id, wall_time=wall_time, time=time, meta=meta_path
    )
    subprocess.call(command, shell=True)
    meta = read_meta(box_id)
    return meta
