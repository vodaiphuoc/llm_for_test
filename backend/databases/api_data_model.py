# -*- coding: utf-8 -*-
from pydantic.dataclasses import dataclass
from pydantic import computed_field, Field, DirectoryPath, FilePath
from typing import List, Optional, Dict, Any, Union
import typing_extensions
import re
import os
from databases.indent_checker import IndentChecker

@dataclass
class UploadFilesBody_Testing():
    """Dataclass for testing purpose only.
    
    Attributes:
        - implement_db (`DB_handler`): Database stores implement codes for serving UI
        - test_cases_db (`DB_handler`): Database stores implement codes and testcase for Agent
        - model (`Agent`): Agent tester, see implement at `backend.llm.agent_tester.py`
        - path2currDir (`DirectoryPath | pathlib.WindowsPath`): Path point to user select forlder, not include target folder name.
        - list_files (`List[str]`): List of file to generate testcases
        - selected_folder_name (`str`): Folder name to select
    """
    implement_db: Any
    test_cases_db: Any
    model: Any
    path2currDir: DirectoryPath = Field(examples=['D:\\Projects\\Test_coverage_LLM\\llm_for_test'])
    list_files: List[str] = Field(examples=[[
        'codes/implements/leet_code.py', 
        'codes/implements/leet_code2.py', 
        'codes/implements/LLM.py', 
        'codes/implements/model_llm.py', 
        'codes/implements/my_function.py', 
        'codes/implements_test_cases/test_my_function.py', 
        'codes/requirements.txt'
    ]])
    selected_folder_name: str = Field(examples=['codes'])


@dataclass
class UploadFilesBody:
    """Dataclass for post request upload file router.
    
    Attributes:
        - path2currDir (str): Path point to user select forlder, not include target folder name.
        - dict_tree (Dict[str,str]): Dictionary represent user repo structure
    
    Example of `dict_tree` ::
    
    {
        "codes":{
            'folderA':'file1.py',
            'folderB': {
                        'file1.py': 'file1.py',
                        'file2.py': 'file2.py'
                    }
                }
    }
    """
    path2currDir: DirectoryPath = Field(examples=['D:\\Projects\\Test_coverage_LLM\\llm_for_test'])
    dict_tree: Dict[str, Union[str,dict]] = Field(examples=[{
                                        'codes': {
                                            'folder_A':'file1.py',
                                            'folder_B': {
                                                'file1.py': 'file1.py',
                                                'file2.py': 'file2.py'
                                            }
                                        }
                                    }]
                                    )


@dataclass
class GenerateTask_Testing:
    """Dataclass for testing purpose only.
    
    Attributes:
        - model (`Agent`): Agent tester, see implement at `backend.llm.agent_tester.py`.
        - test_cases_db (`DB_handler`): Database stores implement codes and testcase for Agent.
        - request_file_dict (`Dict[str,List[str]]`): Relative path from user folder to files.
    """
    model: Any
    run_improve: Any
    test_cases_db: Any
    request_file_dict: Dict[str,List[str]] = Field(examples=[{'file_list': ['llm_for_testPATHSPLITimplementsPATHSPLITleet_code.py']}])

    @computed_field
    @property
    def file_list(self)->List[str]:
        return self.request_file_dict['file_list']


@dataclass
class Script_File:
    file_path: FilePath # original file path to computer's disk
    relative_file_path: str # relative path to project's user folder

    @computed_field
    @property
    def search_file_path(self)->str:
        return re.sub(r'[\\,/]','PATHSPLIT', str(self.file_path))

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
    
    @computed_field
    @property
    def file_content_with_error(self)->Dict[str,str]:
        """Read file from local machine"""
        return IndentChecker.check(self.file_path, self.search_file_path)
    


@dataclass
class File_List:
    list_file: List[Script_File]

