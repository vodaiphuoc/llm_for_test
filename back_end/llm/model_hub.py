
from databases.data_model import LLM_Output
import os
from typing import Literal, List, Dict, Union
from dotenv import load_dotenv
import google.generativeai as genai


class Gemini_Prompts(object):

    prompt = f"""
        - Using pytest package in Python, write a testcase for the following Python file which include
        may contains many Python functions (denote by def keyword). 
        - Don't include content of function in your result, 
        only testing functions. 
        - You must write import functions or classes from 'Module import' and put it in import_module_command of format output
        - Determine what are dependencies have to install outside of Python built-in modules, functions, types... and
        put it in intall_dependencies of format output 
        - Determine what are Python built-in dependencies, put it in built_in_import of format output
        - Below are some examples showing a Original file path, Module import, and Functions and Output format:
        **Example 1
        {{example1}}
        **Example 2
        {{example2}}

        - Now, give output with below tasks:
        {{total_content}}
        """

    example1 = """
**Original file path
user_repo/implements/my_function.py
**Module import:
user_repo.implements.my_function
**Functions
from typing import List

def capital_case(x:str)->str:
    return x.capitalize()

def find_max_element(x: List[int])->int:
    return max(x)

**Output
{        
    'original_file_path':'user_repo/implements/my_function.py'
    'import_module_command': 'from user_repo.implements.my_function import capital_case, find_max_element'
    'intall_dependencies': ''
    'built_in_import': 'from typing import List'
    'test_cases': 
import pytest

def test_capital_case():
    assert capital_case('hello') == 'Hello'
    assert capital_case('world') == 'World'

def test_find_max_element():
    assert find_max_element([1, 2, 3, 4, 5]) == 5
    assert find_max_element([5, 4, 3, 2, 1]) == 5
    assert find_max_element([-1, -2, -3]) == -1

}
"""

    example2 = """
**Original file path
user_repo/implements/model_llm.py
**Module import:
user_repo.implements.model_llm
**Functions
import transformers
from transformers import AutoTokenizer
import torch
from typing import Union, List
from dotenv import load_dotenv
import google.generativeai as genai
import os

class HuggingfaceModel(object):
    def __init__(self, model_url:str, context_length:int):
        self.tokenizer = AutoTokenizer.from_pretrained(model_url)
        self.pipeline = transformers.pipeline(
            task ="text-generation",
            model = model_url,
            torch_dtype = torch.float32,
            device_map = "auto",
        )
        self.context_length = context_length

**Output
{        
    'original_file_path':'user_repo/implements/model_llm.py'
    'import_module_command': 'from user_repo.implements.model_llm import HuggingfaceModel'
    'intall_dependencies': 'import transformers
from transformers import AutoTokenizer
import torch
from dotenv import load_dotenv
import google.generativeai as genai
import pytest'
    'built_in_import': 'from typing import Union, List
import os'
    'test_cases':
@pytest.fixture
def model_url():
    # Returns a valid model URL for testing
    return "gpt2"  # Replace with a suitable test model URL

@pytest.fixture
def context_length():
    # Returns a valid context length for testing
    return 1024

def test_tokenizer_initialization(model_url):
    # Tests if the tokenizer is initialized correctly
    model = HuggingfaceModel(model_url, context_length=100)  # Use a dummy context_length
    assert isinstance(model.tokenizer, AutoTokenizer)

def test_pipeline_initialization(model_url):
    # Tests if the text-generation pipeline is initialized correctly
    model = HuggingfaceModel(model_url, context_length=100)  # Use a dummy context_length
    assert isinstance(model.pipeline, transformers.pipeline)
    assert model.pipeline.task == "text-generation"
    assert model.pipeline.model == model_url

def test_context_length_attribute(model_url, context_length):
    # Tests if the context_length attribute is set correctly
    model = HuggingfaceModel(model_url, context_length)
    assert model.context_length == context_length
"""


class Gemini_Inference(Gemini_Prompts):
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
        total_prompt = self.prompt.format(example1 = self.example1, 
                                          example2 = self.example2, 
                                          total_content = input_prompt)
        final_prompt = self.gemma_prompt.format(input_prompt = total_prompt)
        
        response = self.model.generate_content(contents = final_prompt, 
                                               generation_config = genai.GenerationConfig(
                                                response_schema = LLM_Output,
                                                response_mime_type = "application/json"
                                                )
        )
        return response.text.replace('```the function:','').replace('```','').replace('python','')
