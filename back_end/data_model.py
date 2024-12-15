from pydantic.dataclasses import dataclass
from pydantic import computed_field
from typing import List
import re


@dataclass
class Script_File:
    file_path: str

    @computed_field
    @property
    def save_file_path(self)->str:
        return re.sub(r'[\\,/]','PATHSPLIT', self.file_path)

    @computed_field
    @property
    def file_content(self)->str:
        with open(self.file_path, 'r') as f:
            return f.read()
        
@dataclass
class File_List:
    list_file: List[Script_File]