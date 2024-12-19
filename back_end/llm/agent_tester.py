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


class PyTest_Environment(object):
    def __init__(self,
                 pytest_dir = 'db/pytest_execute_env'
                 ) -> None:
        self.temp_user_repo = pytest_dir + '/user_repo'
        self.log_dir = pytest_dir
        self.pytest_report_dir = pytest_dir + '/report.xml'
        self.python_env_path = pytest_dir+'/testenv/Scripts/python.exe'

        # initialize venv `testenv` when start app
        try:
            os.system(command= f'cd {self.log_dir} && python -m venv testenv')
        except Exception as e:
            print(e)

        # clean everything in user repo
        for _dir in glob.glob(self.temp_user_repo+'/*'):
            shutil.rmtree(_dir, ignore_errors=True)
        # remove all files except Readme.md
        for _file in glob.glob(pathname= '*[.py,.xml]', root_dir=pytest_dir):
            os.remove(pytest_dir+'/'+_file)

    def make_user_repo(self, path2currFolder:str, folder_name:str):
        """this is called in main.py"""
        shutil.copytree(src=path2currFolder+'/'+folder_name,
                        dst = self.temp_user_repo,
                        dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__'))

    def write_testcases_file(self, model_reponse: List[Dict[str,str]])->Union[str, List[str]]:
        """this is called by agent"""
        
        list_llm_output = [Single_LLM_Output(**single_output)
                             for single_output in model_reponse]
        
        content = "\n".join([each_out.tostring() 
                             for each_out in list_llm_output])

        # all outputs stored in one file .py only
        file_name = str(uuid4())+'.py'
        with open(self.log_dir+'/'+file_name, 'w') as f:
            f.write(content)
            f.close()
        return file_name, [each_out.get_dependencies for each_out in list_llm_output]

    def run_make_report(self,
                        test_cases_file_path:str,
                        dependencies: List[str],
                    ):
        """this is called by agent"""
        try:
            if len(dependencies) > 0:
                str_dependencies = ' '.join(dependencies)
                os.system(command= f'{self.python_env_path} -m pip install {str_dependencies}')
            # execute pytest under artificial venv
            os.system(command= f'{self.python_env_path} -m pytest {self.log_dir}/{test_cases_file_path} \
                        --junit-xml={self.pytest_report_dir}')
            return True
        
        except Exception as e:
            print(e)
            return False


class Agent(Gemini_Inference, PyTest_Environment):

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

    def run_batch(self, batch_prompt):
        """Run model in batch"""
        batch_reponse = ''
        for single_prompt in batch_prompt:
            batch_reponse += self(input_prompt = single_prompt)
        return batch_reponse

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
        batch_reponse = self.run_batch(batch_prompt)
        reponse_dict = json.loads(batch_reponse)

        # make one file.py contains all test cases
        (output_temp_file_name, install_dependencies
        ) \
        = self.write_testcases_file(model_reponse = reponse_dict['total_reponse'])

        # run pytest
        status = self.run_make_report(test_cases_file_path= output_temp_file_name)

