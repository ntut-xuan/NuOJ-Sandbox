from flask import Flask
from pytest import fixture, raises

from setting.util import CompilerSetting, Setting

@fixture
def setting(app: Flask) -> Setting:
    with app.app_context():
        setting: Setting = app.config["setting"]
        return setting

class TestSetting:
    def test_setting_object_should_have_correct_sandbox_number(self, setting: Setting):
        assert setting.sandbox_number == 1

    def test_setting_object_should_have_correct_compiler_command_of_submit_code(self, setting: Setting):
        cpp14_compiler_setting = setting.compiler["c++14"]

        assert cpp14_compiler_setting.get_submit_code_compile_command() == "/usr/bin/g++ --std=c++14 submit.cpp -o submit.o"
        assert cpp14_compiler_setting.get_submit_code_execute_command() == "./submit.o"

    def test_setting_object_should_have_correct_compiler_command_of_solution(self, setting: Setting):
        cpp14_compiler_setting = setting.compiler["c++14"]

        assert cpp14_compiler_setting.get_solution_compile_command() == "/usr/bin/g++ --std=c++14 solution.cpp -o solution.o"
        assert cpp14_compiler_setting.get_solution_execute_command() == "./solution.o"

    def test_get_source_filename_with_valid_filename_should_have_correct_filename(self, setting: Setting):
        cpp14_compiler_setting = setting.compiler["c++14"]

        assert cpp14_compiler_setting.get_source_filename("submit") == "submit.cpp"
        assert cpp14_compiler_setting.get_source_filename("solution") == "solution.cpp"
        assert cpp14_compiler_setting.get_source_filename("checker") == "checker.cpp"

    def test_get_source_filename_with_invalid_filename_should_raise_the_exception(self, setting: Setting):
        cpp14_compiler_setting = setting.compiler["c++14"]

        with raises(Exception):
            cpp14_compiler_setting.get_source_filename("invalid_filename")

    def test_get_dist_filename_with_valid_filename_should_have_correct_filename(self, setting: Setting):
        cpp14_compiler_setting = setting.compiler["c++14"]

        assert cpp14_compiler_setting.get_dist_filename("submit") == "submit.o"
        assert cpp14_compiler_setting.get_dist_filename("solution") == "solution.o"
        assert cpp14_compiler_setting.get_dist_filename("checker") == "checker.o"

    def test_get_dist_filename_with_invalid_filename_should_raise_the_exception(self, setting: Setting):
        cpp14_compiler_setting = setting.compiler["c++14"]

        with raises(Exception):
            cpp14_compiler_setting.get_source_filename("invalid_filename")