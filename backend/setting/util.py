import json
from dataclasses import dataclass

@dataclass
class Setting:
    sandbox_number: int
    

class SettingBuilder:
    def from_file(self, file_path: str) -> Setting:
        with open(file_path) as f:
            raw_setting_text: str = f.read()
            setting_dict: dict[str, str] = json.loads(raw_setting_text)
            return self.from_mapping(setting_dict)
            
    def from_mapping(self, mapping: dict[str, str]) -> Setting:
        return Setting(**mapping)
