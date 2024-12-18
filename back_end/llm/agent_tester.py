from .model_hub import ModelHub
from .run_pytest import run_make_report
import os
import pathlib
from typing import Literal, List, Dict
from uuid import uuid4
from loguru import logger

class Agent(object):
    def __init__(self,
                 max_token:int = 3000,
                 log_dir: str = 'db',
                 pytest_report_dir: str = 'db',
                 model_url: Literal['gemini','codellama','openllama','openllama_7b'] = 'gemini'
                 ) -> None:    
        self.prompt = f"""Using pytest package in Python, write a testcase for the following Python file which include
        may contains many Python functions (denote by def keyword). Don't include content of function in your result, 
        only testing functions. You must import functions from 'Module path'
        {{total_content}}
        """

        self.single_content = f"""
Module path:
{{file_path}}
Functions:
{{file_content}}
"""

        self.model = ModelHub.get_model(model= model_url)
        self.max_token = max_token

        if os.path.isdir(log_dir):
            self.log_dir = log_dir
        else:
            os.makedirs(log_dir)
    
    def _write_file(self, content:str):
        file_name = str(uuid4())+'.py'
        with open(self.log_dir+'/'+file_name, 'w') as f:
            f.write(content)
            f.close()
        return file_name


    def run_batch(self, batch_prompt):
        total_response = ''
        for single_prompt in batch_prompt:
            total_response += self.model(input_prompt = \
                                  self.prompt.format(total_content = single_prompt))
        return total_response

    def run(self,
            files_content: List[Dict[str,str]]
            ):
        logger.info('input files_content: ',files_content)
        # prepare input
        batch_prompt = []
        total_content = ''
        for content_dict in files_content:
            current_file_content = self.single_content.format(**content_dict)
            logger.debug('current file content: ',current_file_content)
            if len(total_content.split(' ')) + \
                    len(current_file_content.split(' ')) > self.max_token:
                batch_prompt.append(total_content)
                total_content = ''
                total_content += ' '+current_file_content
            else:
                total_content += ' '+current_file_content

        total_response = self.run_batch(batch_prompt)
        return total_response
        # output_temp_file = self._write_file(total_response)
        # print('output_temp_file: ',output_temp_file)


        # output_files = []
        # for each_file_path in  files_to_test:
        #     file_name = each_file_path.name.split('\\')[-1]
        #     content = self._read_file(each_file_path)
        #     response = self.model(input_prompt = self.prompt.format(file_path = str(each_file_path), 
        #                                                             file_content = content))
        #     output_files.append({
        #         'content': response,
        #         'output_file': test_cases_dir+'/test_'+file_name
        #     })

        
        # run_make_report(logs_file= logs_file, 
        #                 test_cases_dir= test_cases_dir)