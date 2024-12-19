from llm.run_pytest import run_make_report
from databases.data_model import File_List

import os
import shutil
import pathlib
from typing import Literal, List, Dict, Union
from uuid import uuid4
from loguru import logger
from dotenv import load_dotenv
import google.generativeai as genai

class Gemini_Inference(object):
    gemma_prompt = f"<start_of_turn>user\n{{input_prompt}}<end_of_turn><eos>\n"

    def __init__(self,
                model_url:str = 'gemini-1.5-flash',
                context_length:int = 2048):
        super().__init__()

        load_dotenv()
        genai.configure(api_key=os.environ['gemini_key'])
        self.model = genai.GenerativeModel(model_url)
        self.context_length = context_length
    
    def __call__(self,
                 input_prompt: Union[str, List[str]]
                 )->Union[str, List[str]]:

        print('prompt:',input_prompt)       
        final_prompt = self.gemma_prompt.format(input_prompt = input_prompt)
        
        response = self.model.generate_content(contents = final_prompt, 
                                            #    generation_config = genai.GenerationConfig(
                                            #     response_schema = Respone_Schema
                                            #     )
        )
        return response.text.replace('```the function:','').replace('```','').replace('python','')


class Write_User_Repo(object):
    def __init__(self, temp_user_repo:str = 'db/user_repo') -> None:
        print('init this class')
        self.temp_user_repo = temp_user_repo

    def make_user_repo(self, path2currFolder:str, folder_name:str):
        shutil.rmtree(self.temp_user_repo)
        shutil.copytree(src=path2currFolder+'/'+folder_name, 
                        dst = self.temp_user_repo,
                        ignore=shutil.ignore_patterns('__pycache__'))


class Agent(Gemini_Inference, Write_User_Repo):
    prompt = f"""Using pytest package in Python, write a testcase for the following Python file which include
        may contains many Python functions (denote by def keyword). Don't include content of function in your result, 
        only testing functions. You must import functions from 'Module path'
        {{total_content}}
        """
    single_content = f"""
Module path:
{{file_path}}
Functions:
{{file_content}}
"""
    def __init__(self,
                 log_dir: str = 'db',
                 pytest_report_dir: str = 'db',
                 ) -> None:
        super().__init__()
        
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
            total_response += self(input_prompt = \
                                  self.prompt.format(total_content = single_prompt))
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
        
        total_response = self.run_batch(batch_prompt)

        output_temp_file_name = self._write_file(total_response)


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