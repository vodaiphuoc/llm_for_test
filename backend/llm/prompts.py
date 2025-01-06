from abc import ABC, abstractmethod
from typing import List, Any, Union

class Base_Prompts(ABC):
    @abstractmethod
    def input_parse()->int:
        pass

class Improve_Prompts(Base_Prompts):
    prompt = f"""
- Your previous testcase code got below covarage values for each testcase where 
some missing lines in target functions/classes which are not executed when runing testcase with Pytest.

** Orginal code
{{body_content}}

** Your previous testcases
```python
{{prev_testcases}}

** missing lines in original code    
- missing branch type: {{branch_type}}
- missing line had not executed:
```python
{{branch_content}}
    ```

Now, peform belove tasks:
    - Re-write new testcases with suitable input arguemnts for below codes to increase the covarage value of each case and reduce the number of missing lines
using Pytest library only.
{{body_content}}
"""

    def input_parse(body_content:str, 
                    prev_testcases:str, 
                    branch_type:str, 
                    branch_content:str)->str:
        
        return Improve_Prompts.prompt.format(body_content = body_content, 
                                             prev_testcases = prev_testcases,
                                             branch_type = branch_type,
                                             branch_content = branch_content
                                             )

class Normal_Prompts(Base_Prompts):

    single_content = f"""
**Original file path
{{repo_url}}
**Module import:
{{module_path}}
**Functions:
{{file_content}}
"""

    prompt = f"""
- Using pytest package in Python, write a testcase for the following Python file which include
may contains many Python functions (denote by def keyword). 
- Don't include content of function in your result, 
only testing functions. 
- You must write import functions or classes from 'Module import' and put it in `import_module_command` of format output
- Determine what are dependencies have to install outside of Python built-in modules, functions, types... and
put it in `intall_dependencies` of format output with command like `import dependencies_name`
- Determine what are Python built-in dependencies, put it in `built_in_import` of format output
- Determine target of your testcases which is funtion name if it is a normal function or method name of the class if
it is a method inside the class, put it in `target` of format output, 
- Determine `target_type` of the `target`, can be `function` or `method` if it is method of the class
- Below are some examples showing a Original file path, Module import, and Functions and Output format:
**Example 1
{{example1}}
**Example 2
{{example2}}
**Example 3
{{example3}}

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
    'built_in_import': 
from typing import List
import pytest

    'test_cases': [{
        'target': capital_case,
        'target_type': function,
        'test_cases_codes':
def test_capital_case():
    assert capital_case('hello') == 'Hello'
    assert capital_case('world') == 'World'
    },
    {
        'target': find_max_element,
        'target_type': function,
        'test_cases_codes':
def test_find_max_element():
    assert find_max_element([1, 2, 3, 4, 5]) == 5
    assert find_max_element([5, 4, 3, 2, 1]) == 5
    assert find_max_element([-1, -2, -3]) == -1    
    }]

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

    'test_cases': [{
        'target': HuggingfaceModel.__init__,
        'target_type': method,
        'test_cases_codes':
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

def test_context_length_attribute(model_url, context_length):
    # Tests if the context_length attribute is set correctly
    model = HuggingfaceModel(model_url, context_length)
    assert model.context_length == context_length
    }]
}
"""

    example3 = """
**Original file path
user_repo/implements/leet_code.py
**Module import:
user_repo.implements.leet_code
**Functions    
import math
import itertools
import bisect
import collections
import string
import heapq
import functools
import sortedcontainers
from typing import List, Dict, Tuple, Iterator

class Solution_PalindromePairs:
    def __init__(self, task_name:str)->None:
        self.task_name = task_name

    def palindromePairs(self, words: List[str]) -> List[List[int]]:
        ans = []
        dict = {
            word[::-1]: i 
            for i, word in enumerate(words)
        }

        for i, word in enumerate(words):
            if "" in dict and dict[""] != i and word == word[::-1]:
                ans.append([i, dict[""]])

        for j in range(1, len(word) + 1):
            l = word[:j]
            r = word[j:]
            if l in dict and dict[l] != i and r == r[::-1]:
                ans.append([i, dict[l]])
            if r in dict and dict[r] != i and l == l[::-1]:
                ans.append([dict[r], i])

        return ans

**Output
{        
    'original_file_path':'user_repo/implements/leet_code.py'
    'import_module_command': 'from user_repo.implements.leet_code import Solution_PalindromePairs'
    'intall_dependencies': 'import sortedcontainers'
    'built_in_import': 
import math
import itertools
import bisect
import collections
import string
import heapq
import functools
from typing import List, Dict, Tuple, Iterator
import pytest

    'test_cases': [{
        'target': Solution_PalindromePairs.palindromePairs,
        'target_type': 'method',
        'test_cases_codes':
def test_empty_input():
    words = []
    expected = []
    pairs_instance = Solution_PalindromePairs('palind')
    assert pairs_instance.palindromePairs(words) == expected

def test_single_word():
    words = ["a"]
    expected = []
    pairs_instance = Solution_PalindromePairs('palind')
    assert pairs_instance.palindromePairs(words) == expected

def test_no_palindromes():
    words = ["abc", "def", "ghi"]
    expected = []
    pairs_instance = Solution_PalindromePairs('palind')
    assert pairs_instance.palindromePairs(words) == expected

def test_simple_palindromes():
    words = ["a", "abba"]
    expected = [[0, 1], [1, 0]]
    pairs_instance = Solution_PalindromePairs('palind')
    assert pairs_instance.palindromePairs(words) == expected
}
"""
    
    def input_parse(input_data: Union[str, List[str]])->str:
        input_data = "\n".join([Normal_Prompts.single_content.format(**content_dict)
                        for content_dict in input_data
                        ])

        return Normal_Prompts.prompt.format(example1 = Normal_Prompts.example1,
                                            example2 = Normal_Prompts.example2, 
                                            example3 = Normal_Prompts.example3,
                                            total_content = input_data)
