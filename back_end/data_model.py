from pydantic.dataclasses import dataclass
from pydantic import computed_field
from typing import List
import re

DISPLAY_PATTERNS = [
    ('\n','<br>'),
    ('\t','&nbsp;&nbsp;&nbsp;&nbsp;')
]

@dataclass
class Display_Content:
    file_content:str

    @computed_field
    @property
    def display_content(self)->str:
        for old, new in DISPLAY_PATTERNS:
            self.file_content = re.sub(old, new, self.file_content)
        return self.file_content

@dataclass
class Script_File:
    file_path: str

    @computed_field
    @property
    def file_content(self)->str:
        with open(self.file_path, 'r') as f:
            return f.read()
        
@dataclass
class File_List:
    list_file: List[Script_File]