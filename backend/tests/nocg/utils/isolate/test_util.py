import subprocess
from typing import Any
from pathlib import Path

import pytest
from flask import Flask

from utils.isolate.util import (
    generate_options_with_parameter, 
    generate_isolate_init_command, 
    generate_isolate_run_command, 
    generate_isolate_cleanup_command, 
    cleanup_sandbox,
    init_sandbox,
    touch_text_file,
    touch_text_file_by_file_name,
    read_meta,
    read_output,
    compile,
    execute,
    checker
)
from utils.sandbox.enum import CodeType, Language


@pytest.fixture
def box_environment():
    subprocess.call("isolate --box-id=0 --init", shell=True)
    assert Path("/var/local/lib/isolate/0/box").exists()
    yield
    subprocess.call("isolate --box-id=0 --cleanup", shell=True)
    assert not Path("/var/local/lib/isolate/0/box").exists()


@pytest.mark.parametrize(
    "args_key, args_value, excepted_command", 
    [
        ("box_id", 1, "--box-id=1 "),
        ("time", 15, "--time=15 "),
        ("wall_time", 15, "--wall-time=15 "),
        ("extra_time", 15, "--extra-time=15 "),
        ("stack", 32767, "--stack=32767 "),
        ("open_files", 4439, "--open-files=4439 "),
        ("fsize", 4439, "--fsize=4439 "),
        ("stdin", "random_file.py", "--stdin=random_file.py "),
        ("stdout", "random_file.py", "--stdout=random_file.py "),
        ("stderr", "random_file.py", "--stderr=random_file.py "),
        ("meta", "meta.mt", "--meta=meta.mt "),
        ("stderr_to_stdout", True, "--stderr-to-stdout "),
        ("max_processes", True, "--processes "),
        ("share_net", True, "--share-net "),
        ("full_env", True, "--full-env "),
        ("cg", True, "--cg "),
        ("cg_mem", 4096, "--cg-mem=4096 "),
        ("cg_timing", 15, "--cg-timing=15 "),
        ("dir", ("random_file", "rw"), "--dir=random_file:rw "),
        ("mem", 131072, "--mem=131072 "),
    ]
)
def test_generate_options_with_parameter_should_generate_correct_command( app: Flask, args_key, args_value, excepted_command):
    with app.app_context():
        args: dict[str, Any] ={args_key: args_value}
        command: str = generate_options_with_parameter(**args)

        assert command == excepted_command


def test_generate_isolate_initialize_command_should_generate_correct_command(app: Flask):
    with app.app_context():
        isolate_command: str = generate_isolate_init_command(0)

        assert isolate_command == "isolate --box-id=0  --init"


def test_generate_isolate_run_command_should_generate_correct_command(app: Flask):
    with app.app_context():
        isolate_command: str = generate_isolate_run_command("some_execute_command", 0)

        assert isolate_command == "isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- some_execute_command"


def test_generate_isolate_cleanup_command_should_generate_correct_command(app: Flask):
    with app.app_context():
        isolate_command: str = generate_isolate_cleanup_command(0)

        assert isolate_command == "isolate --box-id=0  --cleanup"


def test_init_sandbox_should_init_the_box(app: Flask):
    with app.app_context():
        init_sandbox(0)
        
        assert Path("/var/local/lib/isolate/0/box").exists()
        subprocess.call("isolate --box-id=0 --cleanup", shell=True)
        assert not Path("/var/local/lib/isolate/0/box").exists()


def test_touch_file_should_create_the_file_and_have_correct_data(app: Flask, box_environment: None):
    with app.app_context():
    
        touch_text_file("random_word", CodeType.SUBMIT, "c++14", 0)
    
    assert Path("/var/local/lib/isolate/0/box/submit.cpp").exists()
    assert Path("/var/local/lib/isolate/0/box/submit.cpp").read_text() == "random_word"

    
def test_touch_text_file_by_file_name_should_create_the_file_and_have_correct_data(app: Flask, box_environment: None):
    with app.app_context():

        touch_text_file_by_file_name("random_word", "random.cpp", 0)
    
    assert Path("/var/local/lib/isolate/0/box/random.cpp").exists()
    assert Path("/var/local/lib/isolate/0/box/random.cpp").read_text() == "random_word"


def test_read_meta_should_read_the_correct_meta_data(box_environment: None):
    with open("/var/local/lib/isolate/0/box/meta.mt", "w") as file:
        file.write("random_meta")
        
    meta: str = read_meta(0)
    
    assert meta == "random_meta"


def test_read_output_should_read_the_correct_meta_data(box_environment: None):
    with open("/var/local/lib/isolate/0/box/1.ans", "w") as file:
        file.write("random_answer")
        
    output: str = read_output(0, CodeType.SOLUTION, 0)
    
    assert output == "random_answer"


def test_cleanup_sandbox_should_clean_the_sandbox(app: Flask):
    subprocess.call("isolate --box-id=0 --init", shell=True)
    assert Path("/var/local/lib/isolate/0/box").exists()
    with app.app_context():

        cleanup_sandbox(0)
        
        assert not Path("/var/local/lib/isolate/0/box").exists()


def test_compile_should_compile_the_program(app: Flask, box_environment: None, user_code: str):
    with open("/var/local/lib/isolate/0/box/submit.cpp", "w") as file:
        file.write(user_code)
    with app.app_context():

        meta = compile(CodeType.SUBMIT.value, "c++14", 0)
    
    assert "exitcode:0" in meta


def test_compile_should_generate_the_meta_file(app: Flask, box_environment: None, user_code: str):
    with open("/var/local/lib/isolate/0/box/submit.cpp", "w") as file:
        file.write(user_code)
    with app.app_context():  

        compile(CodeType.SUBMIT.value, "c++14", 0)
    
    assert Path("/var/local/lib/isolate/0/box/submit.compile.mt").exists() 


def test_execute_should_execute_the_program(app: Flask, box_environment: None, user_code: str):
    with open("/var/local/lib/isolate/0/box/submit.cpp", "w") as file:
        file.write(user_code)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ submit.cpp -o submit.o", shell=True)
    with app.app_context():

        meta = execute(CodeType.SUBMIT.value, 0, 5, 5, 131072, "c++14", 0)
    
    assert "exitcode:0" in meta
    with open("/var/local/lib/isolate/0/box/1.out") as file:
        assert file.read() == "5"


def test_execute_with_submit_code_should_generate_output_file(app: Flask, box_environment: None, user_code: str):
    with open("/var/local/lib/isolate/0/box/submit.cpp", "w") as file:
        file.write(user_code)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ submit.cpp -o submit.o", shell=True)
    with app.app_context():
    
        execute(CodeType.SUBMIT.value, 0, 5, 5, 131072, "c++14", 0)
    
    assert Path("/var/local/lib/isolate/0/box/1.out").exists()


def test_execute_with_submit_code_should_generate_meta_file(app: Flask, box_environment: None, user_code: str):
    with open("/var/local/lib/isolate/0/box/submit.cpp", "w") as file:
        file.write(user_code)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ submit.cpp -o submit.o", shell=True)
    with app.app_context():

        execute(CodeType.SUBMIT.value, 0, 5, 5, 131072, "c++14", 0)
    
    assert Path("/var/local/lib/isolate/0/box/1.out.mt").exists()


def test_execute_with_solution_should_generate_answer_file(app: Flask, box_environment: None, user_code: str):
    with open("/var/local/lib/isolate/0/box/solution.cpp", "w") as file:
        file.write(user_code)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ solution.cpp -o solution.o", shell=True)
    with app.app_context():
    
        execute(CodeType.SOLUTION.value, 0, 5, 5, 131072, "c++14", 0)
    
    assert Path("/var/local/lib/isolate/0/box/1.ans").exists()


def test_execute_with_solution_should_generate_meta_file(app: Flask, box_environment: None, user_code: str):
    with open("/var/local/lib/isolate/0/box/solution.cpp", "w") as file:
        file.write(user_code)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ solution.cpp -o solution.o", shell=True)
    with app.app_context():
        
        execute(CodeType.SOLUTION.value, 0, 5, 5, 131072, "c++14", 0)
    
    assert Path("/var/local/lib/isolate/0/box/1.ans.mt").exists()


def test_checker_with_same_output_and_ans_should_return_exitcode_0(app: Flask, box_environment: None, checker_code: str, testlib: str):
    with open("/var/local/lib/isolate/0/box/checker.cpp", "w") as file:
        file.write(checker_code)
    with open("/var/local/lib/isolate/0/box/testlib.h", "w") as file:
        file.write(testlib)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    with open("/var/local/lib/isolate/0/box/1.out", "w") as file:
        file.write("5")
    with open("/var/local/lib/isolate/0/box/1.ans", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ checker.cpp -o checker.o", shell=True)
    with app.app_context():

        meta = checker(0, 5, 5, 0)
    
    assert "exitcode:0" in meta


def test_checker_with_same_output_and_ans_should_return_exitcode_1(app: Flask, box_environment: None, checker_code: str, testlib: str):
    with open("/var/local/lib/isolate/0/box/checker.cpp", "w") as file:
        file.write(checker_code)
    with open("/var/local/lib/isolate/0/box/testlib.h", "w") as file:
        file.write(testlib)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    with open("/var/local/lib/isolate/0/box/1.out", "w") as file:
        file.write("6")
    with open("/var/local/lib/isolate/0/box/1.ans", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ checker.cpp -o checker.o", shell=True)
    with app.app_context():

        meta = checker(0, 5, 5, 0)
    
    assert "exitcode:1" in meta


def test_checker_with_same_output_and_ans_should_return_exitcode_1(app: Flask, box_environment: None, checker_code: str, testlib: str):
    with open("/var/local/lib/isolate/0/box/checker.cpp", "w") as file:
        file.write(checker_code)
    with open("/var/local/lib/isolate/0/box/testlib.h", "w") as file:
        file.write(testlib)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    with open("/var/local/lib/isolate/0/box/1.out", "w") as file:
        file.write("6")
    with open("/var/local/lib/isolate/0/box/1.ans", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ checker.cpp -o checker.o", shell=True)
    with app.app_context():

        checker(0, 5, 5, 0)
    
    assert Path("/var/local/lib/isolate/0/box/1.checker.mt").exists()


def test_checker_with_same_output_and_ans_should_return_exitcode_1(app: Flask, box_environment: None, checker_code: str, testlib: str):
    with open("/var/local/lib/isolate/0/box/checker.cpp", "w") as file:
        file.write(checker_code)
    with open("/var/local/lib/isolate/0/box/testlib.h", "w") as file:
        file.write(testlib)
    with open("/var/local/lib/isolate/0/box/1.in", "w") as file:
        file.write("5")
    with open("/var/local/lib/isolate/0/box/1.out", "w") as file:
        file.write("6")
    with open("/var/local/lib/isolate/0/box/1.ans", "w") as file:
        file.write("5")
    subprocess.call("isolate --box-id=0 --open-files=2048 --full-env --processes  --run -- /usr/bin/g++ checker.cpp -o checker.o", shell=True)
    with app.app_context():

        checker(0, 5, 5, 0)
    
    assert Path("/var/local/lib/isolate/0/box/1.checker.msg").exists()