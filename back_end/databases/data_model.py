from pydantic.dataclasses import dataclass as pd_dataclass
from pydantic import computed_field
from typing import List
import typing_extensions
import re
import os

@pd_dataclass
class Script_File:
    file_path: str # original path to disk
    relative_file_path: str # relative path to project's user folder

    @computed_field
    @property
    def search_file_path(self)->str:
        return re.sub(r'[\\,/]','PATHSPLIT', self.file_path)

    @computed_field
    @property
    def relative_copied_file_path(self)->str:
        user_select_folder = re.split(r'[\\,/]', self.relative_file_path)[0]
        return self.relative_file_path.replace(user_select_folder, 'user_repo')

    @computed_field
    @property
    def import_module(self)->str:
        return re.sub(r'[\\,/]','.', self.relative_copied_file_path).replace('.py','')

    @computed_field
    @property
    def file_content(self)->str:
        """Read file from local machine"""
        with open(self.file_path, 'r') as f:
            return f.read()

@pd_dataclass
class File_List:
    list_file: List[Script_File]

from dataclasses import dataclass

@dataclass
class Single_LLM_Output:
    original_file_path:str
    import_module_command:str
    intall_dependencies: str
    built_in_import:str
    test_cases: str

    def tostring(self)->str:
        return f"""
#{self.original_file_path}
# import functions from modules
{self.import_module_command}
# dependencies to install
{self.intall_dependencies}
# built-in 
{self.built_in_import}
# test cases codes
{self.test_cases}
"""

@dataclass
class LLM_Output:
    total_reponse: List[Single_LLM_Output]

    def tostring(self)->str:
        return 