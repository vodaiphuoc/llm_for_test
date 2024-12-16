from .model_hub import ModelHub
from .run_pytest import run_make_report
import os
import pathlib
from typing import Literal

class Agent(object):
    def __init__(self, model_url: Literal['gemini','codellama','openllama','openllama_7b']) -> None:    
        self.prompt = f"""Using pytest package in Python, write a testcase for the following Python file which include
        may contains many Python functions (denote by def keyword). Don't include content of function in your result, 
        only testing functions. You must import functions from 'Module path'
        Module path:
        {{file_path}}
        Functions:
        {{file_content}}
        
        """
        self.model = ModelHub.get_model(model= model_url)
    
    def _read_file(self, file_path:str)->str:
        with open(file_path, 'r') as f:
            return f.read()
    
    def _write_file(self, content:str, output_file:str):
        with open(output_file, 'w') as f:
            f.write(content)
            f.close()

    def run(self,
            logs_file = 'reports/test.xml',
            input_dir:str = 'codes/implements', 
            test_cases_dir:str = 'codes/implements_test_cases'
            ):
        
        files_to_test = [f for f in pathlib.Path(input_dir).iterdir() \
                            if f.is_file() and '__init__.py' not in str(f)]
        
        output_files = []
        for each_file_path in  files_to_test:
            file_name = each_file_path.name.split('\\')[-1]
            content = self._read_file(each_file_path)
            response = self.model(input_prompt = self.prompt.format(file_path = str(each_file_path), 
                                                                    file_content = content))
            output_files.append({
                'content': response,
                'output_file': test_cases_dir+'/test_'+file_name
            })

        for each_out_file in output_files:
            self._write_file(**each_out_file)
        
        run_make_report(logs_file= logs_file, 
                        test_cases_dir= test_cases_dir)