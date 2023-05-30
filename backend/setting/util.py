import json
from dataclasses import dataclass
from typing import Any


@dataclass
class CompilerSetting:
    file_name: dict[str, Any]
    compile: str
    execute: str
    setting: dict[str, Any]

    def get_submit_code_compile_command(self):
        return self.replace_parameter_in_command(self.compile, "submit")

    def get_submit_code_execute_command(self):
        return self.replace_parameter_in_command(self.execute, "submit")
    
    def get_solution_compile_command(self):
        return self.replace_parameter_in_command(self.compile, "solution")
    
    def get_solution_execute_command(self):
        return self.replace_parameter_in_command(self.execute, "solution")

    def get_checker_compile_command(self):
        return self.replace_parameter_in_command(self.compile, "checker")
    
    def get_checker_execute_command(self):
        return self.replace_parameter_in_command(self.execute, "checker")

    def get_source_filename(self, type: str):
        if type not in self.file_name:
            raise Exception("Unexcepted filename:", type)
        return self.file_name[type]["source"]

    def get_dist_filename(self, type: str):
        assert type in self.file_name
        return self.file_name[type]["dist"]

    def replace_parameter_in_command(self, command: str, type: str):
        command = command.replace("{source}", self.file_name[type]["source"])
        command = command.replace("{dist}", self.file_name[type]["dist"])
        return command


@dataclass
class MinIOConfig:
    enable: bool
    endpoint: str


@dataclass
class Setting:
    sandbox_number: int
    compiler: dict[str, CompilerSetting]
    minio: MinIOConfig


class SettingBuilder:
    def from_file(self, file_path: str) -> Setting:
        with open(file_path) as f:
            raw_setting_text: str = f.read()
            setting_dict: dict[str, str] = json.loads(raw_setting_text)
            return self.from_mapping(setting_dict)
            
    def from_mapping(self, mapping: dict[str, str]) -> Setting:
        return Setting(
            sandbox_number=mapping["sandbox_number"],
            compiler=convert_compiler_dict_to_compiler_setting_object(mapping["compiler"]),
            minio=MinIOConfig(**mapping["minio"])
        )


def convert_compiler_dict_to_compiler_setting_object(compiler: dict[str, Any]):
    compiler_setting_dict: dict[str, CompilerSetting] = {}
    for k, v in compiler.items():
        compiler_setting_dict[k] = CompilerSetting(**v)
    return compiler_setting_dict