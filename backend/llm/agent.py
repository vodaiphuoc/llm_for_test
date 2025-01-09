from llm.gemini import Gemini_Inference
from databases.llm_data_model import Single_LLM_Output
from databases.db import Dependencies_DB_Handler, DB_handler
import glob
import os
import shutil
import pathlib
from typing import Literal, List, Dict, Union
from uuid import uuid4
from loguru import logger
import json
import pathlib
import re
from copy import deepcopy

class PyTest_Environment(object):
    def __init__(self,
                 pytest_dir = 'db/pytest_execute_env',
                 pre_check_pkg_file:str = 'pre_py_pkgs.json'
                 ) -> None:
        self.temp_user_repo = pytest_dir + '/user_repo'
        self.log_dir = pytest_dir
        self.pytest_report_dir = pytest_dir + '/report.xml'
        self.python_env_path = pytest_dir+'/testenv/Scripts/python.exe'
        self.python_env_path = self.python_env_path.replace('/','\\')

        # init db for checking update/install dependencies
        self.pkg_db = Dependencies_DB_Handler()

        # update at start of program
        update_status = self._check_new_pkg_updates(pre_check_pkg_file)
        
        # clean everything in user repo
        for _dir in glob.glob(self.temp_user_repo+'/*'):
            if os.path.isdir(_dir):
                shutil.rmtree(_dir, ignore_errors=True)
            else:
                # this is for file
                os.remove(_dir)

        # remove all files except Readme.md
        for _file in glob.glob(pathname= '*[.py,.xml]', root_dir=pytest_dir):
            os.remove(pytest_dir+'/'+_file)

    def _check_new_pkg_updates(self, pre_check_pkg_file:str):
        with open(pre_check_pkg_file,'r') as fp:
            pre_install_pkgs = json.load(fp)

        to_update_pkgs = []
        for _pkg in pre_install_pkgs:
            if isinstance(self.pkg_db.query_package(_pkg['import_pkg_name']), bool):
                to_update_pkgs.append(_pkg)
        
        if len(to_update_pkgs) > 0:
            print('_check_new_pkg_updates: ',to_update_pkgs)
            try:
                string_new_pkgs = " ".join([ele['PyPi_index'] for ele in to_update_pkgs])
                os.system(command= f'{self.python_env_path} -m pip install {string_new_pkgs}')
                self.pkg_db.insert_files(to_update_pkgs)
                return True

            except Exception as e:
                print(e)
                return False

        return None


    def make_user_repo(self, 
                       path2currFolder: pathlib.WindowsPath,
                       folder_name:str
                       ):
        """this is called in main.py"""
        shutil.copytree(src=path2currFolder / folder_name,
                        dst = self.temp_user_repo,
                        dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__'))

        print('done make repo')
        check_require_txt = [folder_name+'PATHSPLIT'+re.sub(r'[\\,/]','PATHSPLIT', _txt)
            for _txt in glob.glob(pathname = '**/requirements.txt', 
                                  root_dir=self.temp_user_repo,
                                  recursive= True)
        ]
        print('done check .txt')
        return check_require_txt
    

    def _merge_improve_to_original(self, improve_llm_out):
        """Replace function which has missing line with new testcase"""
        assert self.data_repsonse_task['list_llm_output'] is not None
        
        original_llm_output: List[Single_LLM_Output] = self.data_repsonse_task['list_llm_output']

        merged_llm_out = []
        for llm_out in original_llm_output:
            new_testcases = []
            new_testcases.extend(llm_out.test_cases)
            
            for orgin_test in llm_out.test_cases:
                new_testcases_found = [ new_testcase
                    for new_out in improve_llm_out 
                    for new_testcase in new_out.test_cases 
                    if new_testcase['target'] == orgin_test['target']
                ]
                
                if len(new_testcases_found) > 0:
                    new_testcases.extend(new_testcases_found)
        
            merged_llm_out.append(Single_LLM_Output(original_file_path=llm_out.original_file_path, 
                                                    import_module_command=llm_out.import_module_command, 
                                                    intall_dependencies=llm_out.intall_dependencies, 
                                                    built_in_import=llm_out.built_in_import, 
                                                    test_cases=new_testcases)
                                  )

        return "\n".join([each_out.tostring() 
                             for each_out in merged_llm_out])


    def write_testcases_file(self, model_reponse: List[Dict[str,str]])->Union[str, List[str]]:
        """this is called by agent"""
        default_keys_dict = {k:'' for k in Single_LLM_Output.__dataclass_fields__.keys()}

        list_llm_output = [Single_LLM_Output(**single_output)
                           if len(single_output) == len(default_keys_dict)
                           else Single_LLM_Output(**default_keys_dict | single_output)
                             for single_output in model_reponse]
        
        if self.run_improve:
            print('merge new content')
            content = self._merge_improve_to_original(list_llm_output)
        else:
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

        # save target function
        target_funcs = []
        for each_out in list_llm_output:
            cases = [(_case['target'], _case['target_type'], _case['test_cases_codes']) 
                     for _case in each_out.test_cases]
            
            target_funcs.append({each_out.original_file_path: cases})

        return file_name, list(set(duplicated_dependencies)), target_funcs, list_llm_output

    def check_install_dependencies(self, dependencies_list: List[str]):
        # get not installed packages
        to_update_pkgs = []
        for _pkg in dependencies_list:
            if isinstance(self.pkg_db.query_package(_pkg), bool):
                to_update_pkgs.append(_pkg)
        
        print('to_update_pkgs: ',to_update_pkgs)

        # install new packages
        if len(to_update_pkgs) > 0:
            for _new_pkg in to_update_pkgs:
                os.system(command= f'{self.python_env_path} -m pip install {_new_pkg}')

            self.pkg_db.insert_files(to_update_pkgs)
            return {'package to update':to_update_pkgs}
        
        else:
            return {'package to update':'No package to update'}

    def run_make_report(self,
                        test_cases_file_path:str,
                        run_improve:bool
                    ):
        """this is called by agent"""

        # python -m slipcover --json --out slipcover.json -m pytest db\pytest_execute_env\.....py
        slip_cover_output_format = '_slipcover_improve.json' if run_improve else '_slipcover.json'
        slip_cover_output = self.pytest_report_dir.replace('.xml',slip_cover_output_format)
        try:
            # execute pytest under artificial venv
            pytest_cmd = f'{self.python_env_path} -m slipcover --branch --json \
                        --out {slip_cover_output} \
                        -m pytest {self.log_dir}/{test_cases_file_path} \
                        --junit-xml={self.pytest_report_dir}'
            print(pytest_cmd)
            os.system(command= pytest_cmd)
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
    def __init__(self, test_cases_db: DB_handler) -> None:
        super().__init__()
        self.test_cases_db = test_cases_db

        # task results will be assigned here
        self.data_repsonse_task = {
            'prepare_input': None,
            'create_testcases': None,
            'check_dependencies': None,
            'execute_pytest': None
        }
        self.run_improve = False

    def get_prev_cov_result(self):
        """
        Only run with `self.run_improve` is set to True
        
        Returns:
            cov_data = {
                'prev_testcases': ..., 
                'prev_cov': ..., 
                'missing_lines_code': ..., 
        }
        """
        print('===================prepare for run imporving...')
        assert self.data_repsonse_task['target_funcs'] is not None
        assert self.data_repsonse_task['check_dependencies'] is not None
        print('lenght of target function: ',len(self.data_repsonse_task['target_funcs']))

        with open(self.log_dir+'/report_slipcover.json','r') as f:
            cov = json.load(f)

        cov_files = {k.replace('\\','/'):v for k,v in cov['files'].items()}

        # params for target function
        prev_for_improve = []
        for module_dict  in self.data_repsonse_task['target_funcs']:
            for module_path, test_case_list in module_dict.items():

                project_dir2module_path = self.log_dir +'/' + module_path
                splicover_params = cov_files[project_dir2module_path]

                # original content but not executed
                original_content: List[tuple] = self.test_cases_db.get_functions(\
                                                    url = module_path.replace('/','PATHSPLIT').replace('user_repo',''),
                                                    lines = splicover_params["missing_lines"],
                                                    missing_branches = splicover_params['missing_branches'])

                for (_SearchFileUrl, _class_name, _func_name, _func_type,
                      _body_content, _branch_type, _branch_content) in original_content:
                    
                    # not to insert output to DB so just do manual search
                    try:
                        query_testcase = [ test_cases
                                            for (target, target_type, test_cases) in test_case_list 
                                            if (_str_target:= _class_name+'.'+_func_name if _class_name != '' else _func_name) 
                                                in target and _func_type == target_type
                                            ]
                        correspoding_testcase = query_testcase[0] #<-- select first element

                        # search `repo_url`, `module_path` with `_SearchFileUrl`
                        query_result = self.test_cases_db.get_content_from_url(url = _SearchFileUrl,
                                                                                content_type='RawContent')
                        
                        prev_for_improve.append({
                            'repo_url': query_result[0],
                            'module_path': query_result[2],
                            'function_name': _func_name,
                            'body_content': _body_content,
                            'prev_testcases': correspoding_testcase,
                            'branch_type': _branch_type,
                            'branch_content': _branch_content
                        })

                    except IndexError as e:
                        print('index error in manual search: ',e)
                        print('test_case_list: ',test_case_list)
                        print('target in original content: ',_str_target)
        
        print('number cases for improve: ',len(prev_for_improve))
        return prev_for_improve

    # task
    def prepare_input(self,
            request_files: List[str],
            test_cases_db: DB_handler
            ):
        # query raw content in `test_case.db`
        file_contents = [
                {
                    'repo_url': query_result[0],
                    'file_content':query_result[1],
                    'module_path': query_result[2]
                }
                for file_name in request_files
                if len((query_result:= test_cases_db.get_content_from_url(url = file_name,
                                                            content_type='RawContent')
                )) == 3
        ]
        self.data_repsonse_task['prepare_input'] = file_contents
        return True

    # task
    def create_testcases(self):
        assert self.data_repsonse_task['prepare_input'] is not None
        batch_prompt = self.data_repsonse_task['prepare_input']
        # inference
        batch_reponse = self(mode = 'improve' if self.run_improve else 'normal',
                                  input_data = self.get_prev_cov_result() if self.run_improve else batch_prompt
                                  )

        reponse_dict = json.loads(batch_reponse)
        self.data_repsonse_task['create_testcases'] = reponse_dict
        return True

    # task
    def check_dependencies(self):
        assert self.data_repsonse_task['create_testcases'] is not None        
        reponse_dict = self.data_repsonse_task['create_testcases'] 
        # make one file.py contains all test cases
        (output_temp_file_name, install_dependencies, target_funcs, list_llm_output
        ) \
        = self.write_testcases_file(model_reponse = reponse_dict['total_reponse'])

        self.data_repsonse_task['check_dependencies'] = output_temp_file_name
        self.data_repsonse_task['target_funcs'] = target_funcs

        # save `normal` outputs (original testcases) as type `Single_LLM_Output`
        self.data_repsonse_task['list_llm_output'] = list_llm_output

        return self.check_install_dependencies(install_dependencies)

    # task
    def execute_pytest(self):
        assert self.data_repsonse_task['check_dependencies'] is not None        
        output_temp_file_name = self.data_repsonse_task['check_dependencies']

        # output_temp_file_name = '29cbad18-11fd-407b-a1f1-888249c0a9a2.py'
        # run pytest
        status = self.run_make_report(test_cases_file_path= output_temp_file_name, 
                                      run_improve= self.run_improve)

        self.data_repsonse_task['execute_pytest'] = status
        return True