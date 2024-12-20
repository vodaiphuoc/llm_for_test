from llm.model_hub import Gemini_Inference
from databases.data_model import Single_LLM_Output
from databases.db import Dependencies_DB_Handler
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
        self.python_env_path = self.python_env_path.replace('/','\\')

        # init db for checking update/install dependencies
        self.pkg_db = Dependencies_DB_Handler()

        # update at start of program
        new_pkgs = self.pkg_db.check_pkg_updates()
        print('new packages :',new_pkgs)
        # initialize venv `testenv` when start app
        try:
            os.system(command= f'cd {self.log_dir} && python -m venv testenv')
            string_new_pkgs = " ".join([ele['PyPi_index'] for ele in new_pkgs])
            os.system(command= f'{self.python_env_path} -m pip install {string_new_pkgs}')

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

        duplicated_dependencies = []
        for each_out in list_llm_output:
            duplicated_dependencies.extend(each_out.get_dependencies())
        return file_name, list(set(duplicated_dependencies))

    def check_install_dependencies(self, dependencies_list: List[str]):
        # get not installed packages
        to_update_pkgs = []
        for _pkg in dependencies_list:
            if isinstance(self.pkg_db.query_package(_pkg), bool):
                to_update_pkgs.append(_pkg)
        
        # install new packages
        if len(to_update_pkgs) > 0:
            for _new_pkg in to_update_pkgs:
                os.system(command= f'{self.python_env_path} -m pip install {_new_pkg}')

            self.pkg_db.insert_files(to_update_pkgs)
            return {'package to update':to_update_pkgs}
        
        else:
            return {'package to update':'No package to update'}

    def run_make_report(self,
                        test_cases_file_path:str
                    ):
        """this is called by agent"""
        try:
            # execute pytest under artificial venv
            pytest_cmd = f'{self.python_env_path} -m pytest {self.log_dir}/{test_cases_file_path} \
                        --junit-xml={self.pytest_report_dir}'
            print(pytest_cmd)
            os.system(command= pytest_cmd)
            return True
        
        except Exception as e:
            print(e)
            return False

# db/pytest_execute_env/testenv/Scripts/python.exe -m pytest db/29cbad18-11fd-407b-a1f1-888249c0a9a2.py   --junit-xml=db/report.xml


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

        # task results will be assigned here
        self.data_repsonse_task = {
            'prepare_input': None,
            'create_testcases': None,
            'check_dependencies': None,
            'execute_pytest': None
        }

    def run_batch(self, batch_prompt):
        """Run model in batch"""
        batch_reponse = ''
        for single_prompt in batch_prompt:
            batch_reponse += self(input_prompt = single_prompt)
        return batch_reponse

    # task
    def prepare_input(self,
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
        self.data_repsonse_task['prepare_input'] = batch_prompt
        return True

    # task
    def create_testcases(self):
        assert self.data_repsonse_task['prepare_input'] is not None
        batch_prompt = self.data_repsonse_task['prepare_input']
        # inference
        batch_reponse = self.run_batch(batch_prompt)
        reponse_dict = json.loads(batch_reponse)
        self.data_repsonse_task['create_testcases'] = reponse_dict
        return True

    # task
    def check_dependencies(self):
        assert self.data_repsonse_task['create_testcases'] is not None        
        reponse_dict = self.data_repsonse_task['create_testcases'] 
        # make one file.py contains all test cases
        (output_temp_file_name, install_dependencies
        ) \
        = self.write_testcases_file(model_reponse = reponse_dict['total_reponse'])

        self.data_repsonse_task['check_dependencies'] = output_temp_file_name
        return self.check_install_dependencies(install_dependencies)
        # return True

    # task
    def execute_pytest(self):
        assert self.data_repsonse_task['check_dependencies'] is not None        
        output_temp_file_name = self.data_repsonse_task['check_dependencies']

        # output_temp_file_name = '29cbad18-11fd-407b-a1f1-888249c0a9a2.py'
        # run pytest
        status = self.run_make_report(test_cases_file_path= output_temp_file_name)

        self.data_repsonse_task['execute_pytest'] = status
        return True