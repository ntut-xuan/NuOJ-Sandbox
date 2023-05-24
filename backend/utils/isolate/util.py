# -*- coding: utf-8 -*-
"""
The Isolate toolbox by Uriah Xuan for developing NuOJ System.
Due to isolate is a command-execute program, so you can use this tool if you want :D
"""

import subprocess
import os
from utils.sandbox.enum import CodeType, Language

from flask import current_app

from setting.util import CompilerSetting, Setting

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
    mem: int | None = None
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
        "--mem": mem
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
    stderr: str | None = None,
    meta: str | None = None,
    dir: tuple[str, str] | None = None,
    mem: int | None = None,
) -> str:
    control_group: bool = current_app.config["control_group"]
    # --box-id=%d --time=%d --wall-time=%d --cg-mem 256000 -p --full-env --meta='%s' --stdin='%d.in' --stdout='%s' --meta='%s'
    options = generate_options_with_parameter(
        box_id=box_id,
        time=time,
        wall_time=wall_time,
        full_env=True,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        max_processes=True,
        meta=meta,
        open_files=2048,
        cg=control_group,
        dir=dir,
        mem=mem
    )
    return f"isolate {options} --run -- {execute_command}"


def generate_isolate_init_command(box_id: int) -> str:
    control_group: bool = current_app.config["control_group"]
    options = generate_options_with_parameter(cg=control_group, box_id=box_id)
    return f"isolate {options} --init"


def generate_isolate_cleanup_command(box_id: int) -> str:
    control_group: bool = current_app.config["control_group"]
    options = generate_options_with_parameter(cg=control_group, box_id=box_id)
    return f"isolate {options} --cleanup"


def get_compiler_settings():
    compiler_settings: dict[str, CompilerSetting] | None = None

    with current_app.app_context():
        setting: Setting = current_app.config["setting"]
        compiler_settings = setting.compiler

    assert compiler_settings is not None
    return compiler_settings

def get_compile_command(type: str, compiler: str):
    compiler_settings: dict[str, CompilerSetting] = get_compiler_settings()

    if type == CodeType.SUBMIT.value:
        return compiler_settings[compiler].get_submit_code_compile_command()
    
    if type == CodeType.SOLUTION.value:
        return compiler_settings[compiler].get_solution_compile_command()
    
    return compiler_settings[compiler].get_checker_compile_command()

def get_execute_command(type, compiler: str):
    compiler_settings: dict[str, CompilerSetting] = get_compiler_settings()

    if type == CodeType.SUBMIT.value:
        return compiler_settings[compiler].get_submit_code_execute_command()
    
    if type == CodeType.SOLUTION.value:
        return compiler_settings[compiler].get_solution_execute_command()
    
    return compiler_settings[compiler].get_checker_execute_command()


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
    compiler_settings: dict[str, CompilerSetting] = get_compiler_settings()
    source_filename = compiler_settings[compiler].get_source_filename(type.value)
    path = "/var/local/lib/isolate/%d/box/%s" % (box_id, source_filename)
    print("create file at", path)
    with open(path, "w") as code_file:
        code_file.write(text)
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
    return (path, True)


def read_meta(box_id, name="meta") -> str:
    """
    Return the meta file of text, the result after the Isolate run.

        Parameters:
            box_id: The ID of the sandbox you want to read the text of meta file.

        Return:
            A string, the text of meta file on the specific ID of the sandbox.

    """
    meta_path = f"/var/local/lib/isolate/{box_id}/box/{name}.mt"
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
        "%d.out" % (output_index+1)
        if type == CodeType.SUBMIT.value
        else "%d.ans" % (output_index+1)
    )
    output_path = ("/var/local/lib/isolate/%d/box/" + output_file) % (box_id)
    with open(output_path, "r") as code_file:
        return code_file.read()
    
def read_checker_log(output_index, box_id=0) -> str:
    """
    Return the output file of text, the result after the Isolate run.

        Parameters:
            output_index: The index of the output file you want to read the text.
            box_id: The ID of the sandbox you want to read the text of meta file.

        Return:
            A string, the text of output file on the specific ID of the sandbox.

    """
    output_path = f"/var/local/lib/isolate/{box_id}/box/{output_index+1}.checker.msg"
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
    meta_name = f"{type}.compile"
    meta_path = f"/var/local/lib/isolate/{box_id}/box/{meta_name}.mt"
    compile_command = get_compile_command(type, language)
    command = generate_isolate_run_command(
        compile_command, box_id, time=10, meta=meta_path
    )
    touch_text_file_by_file_name("init", f"{meta_name}.mt", box_id)
    subprocess.call(command, shell=True)
    return read_meta(box_id, name=meta_name)


def execute(type, test_case_index, time, wall_time, memory, language, box_id=0) -> str:
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
    exec_command = get_execute_command(type, language)
    extension = "out" if CodeType.SUBMIT.value == type else "ans"
    meta_name = f"{test_case_index+1}.{extension}"
    meta_path = f"/var/local/lib/isolate/{box_id}/box/{meta_name}.mt"
    touch_text_file_by_file_name("init", f"{meta_name}.mt", box_id)
    input_file = f"{test_case_index+1}.in"
    output_file = f"{test_case_index+1}.{extension}"
    command = generate_isolate_run_command(
        exec_command, box_id, wall_time, time, input_file, output_file, meta=meta_path, mem=memory
    )
    touch_text_file_by_file_name("init", output_file, box_id)
    
    print(f"Execute testcase {test_case_index+1}")
    subprocess.call(command, shell=True)
    print(f"read meta {meta_name}.mt")
    meta = read_meta(box_id, name=meta_name)
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
    meta_name = f"{test_case_index+1}.checker"
    meta_path = f"/var/local/lib/isolate/{box_id}/box/{meta_name}.mt"
    checker_msg_file_name = f"{meta_name}.msg"
    touch_text_file_by_file_name("init", f"{meta_name}.mt", box_id)
    touch_text_file_by_file_name("init", checker_msg_file_name, box_id)
    
    input_name = f"{test_case_index+1}.in"
    output_name = f"{test_case_index+1}.out"
    answer_name = f"{test_case_index+1}.ans"
    execute_command = f"{code_output} {input_name} {output_name} {answer_name}"
    command = generate_isolate_run_command(
        execute_command, box_id, wall_time=wall_time, time=time, meta=meta_path, stderr=checker_msg_file_name, mem=131072
    )
    
    subprocess.call(command, shell=True)
    meta = read_meta(box_id, name=meta_name)
    return meta
