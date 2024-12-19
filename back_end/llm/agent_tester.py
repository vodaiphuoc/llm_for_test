from llm.run_pytest import run_make_report
from llm.model_hub import Gemini_Inference
from databases.data_model import Single_LLM_Output
import glob
import os
import shutil
import pathlib
from typing import Literal, List, Dict, Union
from uuid import uuid4
from loguru import logger
import json


class Write_User_Repo(object):
    def __init__(self, temp_user_repo:str = 'db/user_repo') -> None:
        print('init this class')
        self.temp_user_repo = temp_user_repo

    def make_user_repo(self, path2currFolder:str, folder_name:str):
        for _dir in glob.glob(self.temp_user_repo+'/*'):
            shutil.rmtree(_dir, ignore_errors=True)
        
        shutil.copytree(src=path2currFolder+'/'+folder_name,
                        dst = self.temp_user_repo,
                        dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__'))


class Agent(Gemini_Inference, Write_User_Repo):

    single_content = f"""
**Original file path
{{repo_url}}
**Module import:
{{module_path}}
**Functions:
{{file_content}}
"""
    def __init__(self,
                 log_dir: str = 'db',
                 pytest_report_dir: str = 'db/report.xml',
                 ) -> None:
        super().__init__()
        
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
            
        self.log_dir = log_dir
        self.pytest_report_dir = pytest_report_dir

    def _write_file(self, model_reponse: List[Dict[str,str]]):
        content = "\n".join([Single_LLM_Output(**single_output).tostring() 
                             for single_output in model_reponse])

        file_name = str(uuid4())+'.py'
        with open(self.log_dir+'/'+file_name, 'w') as f:
            f.write(content)
            f.close()
        return file_name

    def run_batch(self, batch_prompt):
        """Run model in batch"""
        total_response = ''
        for single_prompt in batch_prompt:
            total_response += self(input_prompt = single_prompt)
        return total_response

    def run(self,
            files_content: List[Dict[str,str]]
            ):
        # prepare input
        batch_prompt = []
        total_content = ''
        for content_dict in files_content:
            current_file_content = self.single_content.format(**content_dict)
            if len(total_content.split(' ')) + \
                    len(current_file_content.split(' ')) > self.context_length:
                batch_prompt.append(total_content)
                total_content = ''
                total_content += ' '+current_file_content
            else:
                total_content += ' '+current_file_content
        batch_prompt.append(total_content)
        

        # inference
        total_response = self.run_batch(batch_prompt)

        reponse_dict = json.loads(total_response)
        print('reponse_dict: ',reponse_dict)

        # make one file.py contains all test cases
        output_temp_file_name = self._write_file(model_reponse = reponse_dict['total_reponse'])

        # # run pytest
        # status = run_make_report(logs_file= self.pytest_report_dir, 
        #                 test_cases_file_path= output_temp_file_name)

