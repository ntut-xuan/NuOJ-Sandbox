from flask import Flask
from pytest import fixture

from setting.util import CompilerSetting, Setting

@fixture
def setting(app: Flask) -> Setting:
    with app.app_context():
        setting: Setting = app.config["setting"]
        return setting

def test_setting_object_should_have_correct_sandbox_number(setting: Setting):
    assert setting.sandbox_number == 1

def test_setting_object_should_have_correct_compiler_command_of_submit_code(setting: Setting):
    cpp14_compiler_setting = setting.compiler["c++14"]

    assert cpp14_compiler_setting.get_submit_code_compile_command() == "/usr/bin/g++ --std=c++14 submit.cpp -o submit.o"
    assert cpp14_compiler_setting.get_submit_code_execute_command() == "./submit.o"

def test_setting_object_should_have_correct_compiler_command_of_solution(setting: Setting):
    cpp14_compiler_setting = setting.compiler["c++14"]

    assert cpp14_compiler_setting.get_solution_compile_command() == "/usr/bin/g++ --std=c++14 solution.cpp -o solution.o"
    assert cpp14_compiler_setting.get_solution_execute_command() == "./solution.o"